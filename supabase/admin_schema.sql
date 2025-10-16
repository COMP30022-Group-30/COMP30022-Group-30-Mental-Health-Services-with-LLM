-- =============================================================================
-- Supabase Admin Schema
-- =============================================================================
-- This file recreates the Django admin data model inside Supabase so the
-- React portal can talk to Supabase directly (no Django in the loop).
-- Run it once with the service-role key:
--
--   supabase db push --file supabase/admin_schema.sql
--
-- or paste the statements into the Supabase SQL editor.
-- =============================================================================

create extension if not exists "pgcrypto";

-- -----------------------------------------------------------------------------
-- Enum types
-- -----------------------------------------------------------------------------
do $$
begin
  if not exists (select 1 from pg_type where typname = 'admin_role') then
    create type public.admin_role as enum (
      'user',
      'provider',
      'moderator',
      'admin',
      'super_admin'
    );
  end if;
end$$;

do $$
begin
  if not exists (select 1 from pg_type where typname = 'provider_status') then
    create type public.provider_status as enum (
      'pending',
      'approved',
      'disabled',
      'rejected'
    );
  end if;
end$$;

do $$
begin
  if not exists (select 1 from pg_type where typname = 'service_status') then
    create type public.service_status as enum (
      'draft',
      'pending',
      'approved',
      'disabled',
      'rejected'
    );
  end if;
end$$;

-- -----------------------------------------------------------------------------
-- Helpers
-- -----------------------------------------------------------------------------
create or replace function public.touch_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = timezone('utc', now());
  return new;
end;
$$;

-- -----------------------------------------------------------------------------
-- Tables
-- -----------------------------------------------------------------------------
create table if not exists public.admin_profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  username text unique not null,
  email text not null,
  first_name text,
  last_name text,
  role public.admin_role not null default 'user',
  phone_number text,
  job_title text,
  organisation text,
  notes text,
  is_active boolean not null default true,
  last_login timestamptz,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create trigger trg_admin_profiles_updated
before update on public.admin_profiles
for each row
execute function public.touch_updated_at();

create table if not exists public.provider_profiles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  display_name text not null,
  contact_email text,
  phone_number text,
  website text,
  description text,
  address text,
  status public.provider_status not null default 'pending',
  reviewed_by uuid references auth.users(id),
  reviewed_at timestamptz,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create trigger trg_provider_profiles_updated
before update on public.provider_profiles
for each row
execute function public.touch_updated_at();

create table if not exists public.service_categories (
  id uuid primary key default gen_random_uuid(),
  name text unique not null,
  slug text unique not null,
  description text,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create trigger trg_service_categories_updated
before update on public.service_categories
for each row
execute function public.touch_updated_at();

create table if not exists public.services (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  slug text unique not null,
  summary text,
  description text not null,
  status public.service_status not null default 'pending',
  approval_notes text,
  provider_id uuid references public.provider_profiles(id),
  category_id uuid references public.service_categories(id),
  created_by uuid references auth.users(id),
  updated_by uuid references auth.users(id),
  approved_by uuid references auth.users(id),
  approved_at timestamptz,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create trigger trg_services_updated
before update on public.services
for each row
execute function public.touch_updated_at();

create or replace function public.current_admin_role()
returns text
language sql
stable
security definer
set search_path = public
as $$
  select role::text
  from public.admin_profiles
  where user_id = auth.uid();
$$;

-- -----------------------------------------------------------------------------
-- Views
-- -----------------------------------------------------------------------------
create or replace view public.admin_users_view as
select
  ap.user_id as id,
  ap.username,
  ap.email,
  ap.first_name,
  ap.last_name,
  ap.role,
  ap.phone_number,
  ap.job_title,
  ap.organisation,
  ap.notes,
  ap.is_active,
  ap.last_login,
  u.created_at as date_joined,
  u.last_sign_in_at,
  ap.created_at,
  ap.updated_at
from public.admin_profiles ap
join auth.users u on u.id = ap.user_id;

create or replace view public.provider_profiles_view as
select
  pp.id,
  pp.display_name,
  pp.contact_email,
  pp.phone_number,
  pp.website,
  pp.description,
  pp.address,
  pp.status,
  pp.reviewed_by,
  pp.reviewed_at,
  pp.created_at,
  pp.updated_at,
  jsonb_build_object(
    'id', ap.user_id,
    'username', ap.username,
    'email', ap.email,
    'role', ap.role,
    'first_name', ap.first_name,
    'last_name', ap.last_name
  ) as user
from public.provider_profiles pp
left join public.admin_profiles ap on ap.user_id = pp.user_id;

create or replace view public.services_view as
select
  s.id,
  s.name,
  s.slug,
  s.summary,
  s.description,
  s.status,
  s.approval_notes,
  s.provider_id,
  s.category_id,
  s.created_by,
  s.updated_by,
  s.approved_by,
  s.approved_at,
  s.created_at,
  s.updated_at,
  to_jsonb(ppv) as provider,
  to_jsonb(sc) as category
from public.services s
left join public.provider_profiles_view ppv on ppv.id = s.provider_id
left join public.service_categories sc on sc.id = s.category_id;

-- -----------------------------------------------------------------------------
-- Triggers & helpers to keep admin_profiles in sync with auth metadata
-- -----------------------------------------------------------------------------
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  base_username text;
  generated_username text;
  suffix integer := 0;
  desired_role text;
  inserted boolean := false;
  now_ts timestamptz := timezone('utc', now());
begin
  base_username := coalesce(
    nullif(trim(coalesce(new.raw_user_meta_data->>'username', '')), ''),
    nullif(split_part(coalesce(new.email, ''), '@', 1), ''),
    'user_' || substring(cast(new.id as text) from 1 for 8)
  );
  generated_username := base_username;

  desired_role := lower(nullif(trim(coalesce(new.raw_user_meta_data->>'role', '')), ''));
  if desired_role not in ('user', 'provider', 'moderator', 'admin', 'super_admin') then
    desired_role := 'user';
  end if;

  while not inserted loop
    begin
      insert into public.admin_profiles (user_id, username, email, role, created_at, updated_at)
      values (
        new.id,
        generated_username,
        coalesce(new.email, ''),
        desired_role::public.admin_role,
        now_ts,
        now_ts
      )
      on conflict (user_id) do update
        set
          username = excluded.username,
          email = excluded.email,
          role = excluded.role,
          updated_at = excluded.updated_at;
      inserted := true;
    exception
      when unique_violation then
        if position('admin_profiles_username_key' in lower(SQLERRM)) > 0 then
          suffix := suffix + 1;
          generated_username := base_username || '_' || suffix;
        else
          raise warning 'handle_new_user unique violation for user %: %', new.id, SQLERRM;
          return new;
        end if;
      when others then
        raise warning 'handle_new_user failed for user %: %', new.id, SQLERRM;
        return new;
    end;
  end loop;

  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;

create trigger on_auth_user_created
after insert on auth.users
for each row execute function public.handle_new_user();

-- -----------------------------------------------------------------------------
-- Row Level Security
-- -----------------------------------------------------------------------------
alter table public.admin_profiles enable row level security;
alter table public.provider_profiles enable row level security;
alter table public.service_categories enable row level security;
alter table public.services enable row level security;

create policy admin_select_admin_profiles
on public.admin_profiles
for select
using (
  public.current_admin_role() in ('moderator', 'admin', 'super_admin')
  or auth.role() = 'service_role'
);

create policy admin_mutate_admin_profiles
on public.admin_profiles
for all
using (public.current_admin_role() = 'super_admin' or auth.role() = 'service_role')
with check (public.current_admin_role() = 'super_admin' or auth.role() = 'service_role');

create policy admin_manage_provider_profiles
on public.provider_profiles
for all
using (public.current_admin_role() in ('moderator', 'admin', 'super_admin') or auth.role() = 'service_role')
with check (public.current_admin_role() in ('moderator', 'admin', 'super_admin') or auth.role() = 'service_role');

create policy admin_manage_service_categories
on public.service_categories
for all
using (public.current_admin_role() in ('admin', 'super_admin') or auth.role() = 'service_role')
with check (public.current_admin_role() in ('admin', 'super_admin') or auth.role() = 'service_role');

create policy admin_manage_services
on public.services
for all
using (public.current_admin_role() in ('moderator', 'admin', 'super_admin') or auth.role() = 'service_role')
with check (public.current_admin_role() in ('moderator', 'admin', 'super_admin') or auth.role() = 'service_role');

-- Allow read access for signed-in admins on the convenience views.
grant usage on schema public to anon, authenticated, service_role;
grant select on public.admin_users_view to authenticated, service_role;
grant select on public.provider_profiles_view to authenticated, service_role;
grant select on public.services_view to authenticated, service_role;
