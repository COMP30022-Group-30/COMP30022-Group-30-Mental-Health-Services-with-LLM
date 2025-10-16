# Admin Portal Setup

The Django-based admin API has been retired. Admin management now happens
directly in Supabase and the React admin UI talks to Supabase REST/auth.
Follow these steps to configure Supabase and the frontend.

## 1. Apply the Supabase schema

Run the SQL bundle at `supabase/admin_schema.sql` using the Supabase CLI or SQL editor:

```bash
supabase db push --file supabase/admin_schema.sql
```

This script:

- Introduces enum types for admin/provider/service roles
- Creates Supabase tables mirroring the former Django models
- Adds views the frontend consumes (users, providers, services)
- Sets up RLS policies so only authenticated admins can mutate data
- Automatically provisions an `admin_profiles` row when a new Supabase user is created

## 2. Seed an initial super admin account

Use the Supabase Auth dashboard (or CLI) to create a user and mark it as a
`super_admin`. The quickest path is to set the `role` field inside
`auth.users.raw_user_meta_data` before inserting, or update the
`admin_profiles.role` column afterwards:

```sql
update admin_profiles
set role = 'super_admin'
where email = 'superadmin@example.com';
```

Record the email/password—they will be used to sign in via the React admin portal.

## 3. Frontend environment

Update `frontend/web/.env` with your Supabase configuration:

```
VITE_SUPABASE_URL=https://{project-id}.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_SUPABASE_SERVICE_KEY=your-service-role-key  # required for admin CRUD helpers
VITE_SHOW_ADMIN_LINK=1
```

> ⚠️ The service-role key grants elevated privileges; keep this file out of version
> control and restrict distribution to trusted administrators.

## 4. Start the apps

Backend (Django is still used for the chat APIs, but no longer for admin):

```bash
cd Backened
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Frontend:

```bash
cd frontend/web
npm install
npm run dev
```

Navigate to `http://localhost:5173/admin` and sign in with the super admin account.

## 5. Testing

- Backend: `python manage.py test` (admin tests are skipped—admin logic now lives in Supabase)
- Frontend: `npm test`

E2E tests that rely on Django admin endpoints should be updated to seed/fetch data directly from Supabase.
