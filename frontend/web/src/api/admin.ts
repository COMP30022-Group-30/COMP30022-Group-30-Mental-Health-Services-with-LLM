import type {
  AdminRole,
  AdminUser,
  Paginated,
  ProviderProfile,
  Service,
  ServiceCategory,
  AdminProfile,
} from '@/types/admin';
import { getSupabaseClient } from '@/auth/supabaseClient';
import { getSupabaseAdminClient } from '@/admin/supabaseAdminClient';

type AdminUserRow = {
  id: string;
  username: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  role: AdminRole;
  phone_number: string | null;
  job_title: string | null;
  organisation: string | null;
  notes: string | null;
  is_active: boolean;
  last_login: string | null;
  last_sign_in_at: string | null;
  date_joined: string;
  created_at: string;
  updated_at: string;
};

type ProviderRow = {
  id: string;
  display_name: string;
  contact_email: string | null;
  phone_number: string | null;
  website: string | null;
  description: string | null;
  address: string | null;
  status: ProviderProfile['status'];
  reviewed_by: string | null;
  reviewed_at: string | null;
  created_at: string;
  updated_at: string;
  user: null | {
    id: string;
    username: string;
    email: string;
    role: AdminRole;
    first_name: string | null;
    last_name: string | null;
  };
};

type ServiceRow = {
  id: string;
  name: string;
  slug: string;
  summary: string | null;
  description: string;
  status: Service['status'];
  approval_notes: string | null;
  provider_id: string | null;
  category_id: string | null;
  created_by: string | null;
  updated_by: string | null;
  approved_by: string | null;
  approved_at: string | null;
  created_at: string;
  updated_at: string;
  provider: ProviderRow | null;
  category: ServiceCategory | null;
};

type PaginationParams = {
  search?: string;
  status?: string;
  page?: number;
  page_size?: number;
  category?: string;
};

function requireClient() {
  const supabase = getSupabaseClient();
  if (!supabase) throw new Error('Supabase client is not configured.');
  return supabase;
}

function requireAdminClient() {
  const supabase = getSupabaseAdminClient();
  if (!supabase) throw new Error('Supabase service client is not configured.');
  return supabase;
}

function mapAdmin(row: AdminUserRow): AdminUser {
  return {
    id: row.id,
    username: row.username,
    email: row.email,
    first_name: row.first_name ?? '',
    last_name: row.last_name ?? '',
    is_active: row.is_active,
    date_joined: row.date_joined,
    last_login: row.last_login,
    last_sign_in_at: row.last_sign_in_at,
    profile: {
      role: row.role,
      phone_number: row.phone_number,
      job_title: row.job_title,
      organisation: row.organisation,
      notes: row.notes,
      created_at: row.created_at,
      updated_at: row.updated_at,
    },
  };
}

async function fetchAdminById(id: string): Promise<AdminUser> {
  const client = requireClient();
  const { data, error } = await client
    .from<AdminUserRow>('admin_users_view')
    .select('*')
    .eq('id', id)
    .single();
  if (error || !data) throw new Error(error?.message ?? 'Admin user not found.');
  return mapAdmin(data);
}

async function fetchProviderById(id: string): Promise<ProviderProfile> {
  const supabase = requireClient();
  const { data, error } = await supabase
    .from<ProviderRow>('provider_profiles_view')
    .select('*')
    .eq('id', id)
    .single();
  if (error || !data) throw new Error(error?.message ?? 'Provider not found.');
  return {
    id: data.id,
    user: data.user,
    display_name: data.display_name,
    contact_email: data.contact_email,
    phone_number: data.phone_number,
    website: data.website,
    description: data.description,
    address: data.address,
    status: data.status,
    reviewed_by: data.reviewed_by,
    reviewed_at: data.reviewed_at,
    created_at: data.created_at,
    updated_at: data.updated_at,
  };
}

async function fetchServiceById(id: string): Promise<Service> {
  const supabase = requireClient();
  const { data, error } = await supabase
    .from<ServiceRow>('services_view')
    .select('*')
    .eq('id', id)
    .single();
  if (error || !data) throw new Error(error?.message ?? 'Service not found.');
  return {
    id: data.id,
    name: data.name,
    slug: data.slug,
    summary: data.summary,
    description: data.description,
    status: data.status,
    approval_notes: data.approval_notes,
    provider_id: data.provider_id,
    category_id: data.category_id,
    provider: data.provider
      ? {
          id: data.provider.id,
          user: data.provider.user,
          display_name: data.provider.display_name,
          contact_email: data.provider.contact_email,
          phone_number: data.provider.phone_number,
          website: data.provider.website,
          description: data.provider.description,
          address: data.provider.address,
          status: data.provider.status,
          reviewed_by: data.provider.reviewed_by,
          reviewed_at: data.provider.reviewed_at,
          created_at: data.provider.created_at,
          updated_at: data.provider.updated_at,
        }
      : null,
    category: data.category,
    created_by: data.created_by,
    updated_by: data.updated_by,
    approved_by: data.approved_by,
    approved_at: data.approved_at,
    created_at: data.created_at,
    updated_at: data.updated_at,
  };
}

async function getCurrentUserId(): Promise<string | null> {
  const supabase = requireClient();
  const { data, error } = await supabase.auth.getUser();
  if (error) throw new Error(error.message);
  return data.user?.id ?? null;
}

export type AdminProfileUpdate = Partial<Omit<AdminUser, 'profile'>> & {
  profile?: Partial<AdminProfile>;
};

export type LoginPayload = { username: string; password: string };
export type LoginResponse = { user: AdminUser };

export async function loginAdmin(payload: LoginPayload): Promise<LoginResponse> {
  const supabase = requireClient();
  const identifier = payload.username.trim();
  if (!identifier) throw new Error('Email or username is required.');

  let email = identifier;
  if (!identifier.includes('@')) {
    const adminClient = requireAdminClient();
    const { data, error } = await adminClient
      .from<{ email: string }>('admin_profiles')
      .select('email')
      .eq('username', identifier)
      .single();
    if (error || !data) throw new Error('Unknown administrator username.');
    email = data.email;
  }

  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password: payload.password,
  });

  if (error) throw new Error(error.message);
  if (!data.session?.user?.id) throw new Error('Invalid Supabase response.');

  const user = await fetchAdminById(data.session.user.id);
  if (!['moderator', 'admin', 'super_admin'].includes(user.profile.role)) {
    await supabase.auth.signOut();
    throw new Error('This account does not have administrator permissions.');
  }

  return { user };
}

export async function refreshAdmin(): Promise<LoginResponse> {
  const supabase = requireClient();
  const { data, error } = await supabase.auth.getSession();
  if (error) throw new Error(error.message);
  const userId = data.session?.user?.id;
  if (!userId) throw new Error('No active admin session.');
  const user = await fetchAdminById(userId);
  return { user };
}

export async function logoutAdmin(): Promise<void> {
  const supabase = requireClient();
  await supabase.auth.signOut();
}

export async function fetchAdminMe(): Promise<AdminUser> {
  const supabase = requireClient();
  const { data, error } = await supabase.auth.getSession();
  if (error) throw new Error(error.message);
  const id = data.session?.user?.id;
  if (!id) throw new Error('Not signed in.');
  return fetchAdminById(id);
}

export async function updateAdminProfile(patch: AdminProfileUpdate): Promise<AdminUser> {
  const supabase = requireClient();
  const { data: session } = await supabase.auth.getSession();
  const id = session.session?.user?.id;
  if (!id) throw new Error('Not signed in.');

  const adminClient = requireAdminClient();
  const profileUpdate: Record<string, unknown> = {};
  if (typeof patch.username === 'string') profileUpdate.username = patch.username;
  if (typeof patch.email === 'string') profileUpdate.email = patch.email;
  if (typeof patch.first_name === 'string') profileUpdate.first_name = patch.first_name;
  if (typeof patch.last_name === 'string') profileUpdate.last_name = patch.last_name;
  if (patch.profile?.role) profileUpdate.role = patch.profile.role;
  if (patch.profile?.phone_number !== undefined) profileUpdate.phone_number = patch.profile.phone_number;
  if (patch.profile?.job_title !== undefined) profileUpdate.job_title = patch.profile.job_title;
  if (patch.profile?.organisation !== undefined) profileUpdate.organisation = patch.profile.organisation;
  if (patch.profile?.notes !== undefined) profileUpdate.notes = patch.profile.notes;

  if (Object.keys(profileUpdate).length > 0) {
    const { error } = await adminClient
      .from('admin_profiles')
      .update(profileUpdate)
      .eq('user_id', id);
    if (error) throw new Error(error.message);
  }

  if (patch.email || patch.first_name || patch.last_name) {
    const { error: userError } = await supabase.auth.updateUser({
      email: patch.email,
      data: {
        first_name: patch.first_name,
        last_name: patch.last_name,
        username: patch.username,
      },
    });
    if (userError) throw new Error(userError.message);
  }

  return fetchAdminById(id);
}

function buildPagination(params: PaginationParams) {
  const pageSize = Math.max(1, params.page_size ?? 25);
  const page = Math.max(1, params.page ?? 1);
  return {
    page,
    pageSize,
    rangeStart: (page - 1) * pageSize,
    rangeEnd: (page - 1) * pageSize + (pageSize - 1),
  };
}

export async function listUsers(params: PaginationParams = {}): Promise<Paginated<AdminUser>> {
  const supabase = requireClient();
  const { rangeStart, rangeEnd, page } = buildPagination(params);
  let query = supabase
    .from<AdminUserRow>('admin_users_view')
    .select('*', { count: 'exact' })
    .order('created_at', { ascending: false })
    .range(rangeStart, rangeEnd);

  if (params.search) {
    const term = `%${params.search}%`;
    query = query.or(`username.ilike.${term},email.ilike.${term},first_name.ilike.${term},last_name.ilike.${term}`);
  }

  const { data, error, count } = await query;
  if (error) throw new Error(error.message);
  const results = (data ?? []).map(mapAdmin);

  const total = count ?? results.length;
  return {
    count: total,
    results,
    previous: page > 1 ? String(page - 1) : null,
    next: rangeEnd + 1 < total ? String(page + 1) : null,
  };
}

type CreateUserPayload = {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
  role: AdminRole;
};

type UpdateUserPayload = Partial<CreateUserPayload> & { is_active?: boolean };

export async function createUser(payload: CreateUserPayload): Promise<AdminUser> {
  const adminClient = requireAdminClient();

  const { data, error } = await adminClient.auth.admin.createUser({
    email: payload.email,
    password: payload.password,
    email_confirm: true,
    user_metadata: {
      username: payload.username,
      first_name: payload.first_name,
      last_name: payload.last_name,
    },
  });
  if (error || !data.user?.id) throw new Error(error?.message ?? 'Failed to create admin user.');

  const { error: profileError } = await adminClient
    .from('admin_profiles')
    .update({
      username: payload.username,
      email: payload.email,
      first_name: payload.first_name,
      last_name: payload.last_name,
      role: payload.role,
      is_active: true,
    })
    .eq('user_id', data.user.id);
  if (profileError) throw new Error(profileError.message);

  return fetchAdminById(data.user.id);
}

export async function updateUser(id: string, payload: UpdateUserPayload): Promise<AdminUser> {
  const adminClient = requireAdminClient();

  const metadata: Record<string, unknown> = {};
  if (payload.first_name !== undefined) metadata.first_name = payload.first_name;
  if (payload.last_name !== undefined) metadata.last_name = payload.last_name;
  if (payload.username !== undefined) metadata.username = payload.username;

  if (payload.email || Object.keys(metadata).length > 0) {
    const { error } = await adminClient.auth.admin.updateUserById(id, {
      email: payload.email,
      user_metadata: metadata,
    });
    if (error) throw new Error(error.message);
  }

  const profileUpdate: Record<string, unknown> = {};
  if (payload.username !== undefined) profileUpdate.username = payload.username;
  if (payload.email !== undefined) profileUpdate.email = payload.email;
  if (payload.first_name !== undefined) profileUpdate.first_name = payload.first_name;
  if (payload.last_name !== undefined) profileUpdate.last_name = payload.last_name;
  if (payload.role !== undefined) profileUpdate.role = payload.role;
  if (payload.is_active !== undefined) profileUpdate.is_active = payload.is_active;

  if (Object.keys(profileUpdate).length > 0) {
    const { error } = await adminClient
      .from('admin_profiles')
      .update(profileUpdate)
      .eq('user_id', id);
    if (error) throw new Error(error.message);
  }

  return fetchAdminById(id);
}

export async function deleteUser(id: string): Promise<void> {
  const adminClient = requireAdminClient();
  const { error } = await adminClient.auth.admin.deleteUser(id);
  if (error) throw new Error(error.message);
}

export async function listAdmins(params: PaginationParams = {}): Promise<Paginated<AdminUser>> {
  const result = await listUsers(params);
  return {
    ...result,
    results: result.results.filter((user) => ['moderator', 'admin', 'super_admin'].includes(user.profile.role)),
  };
}

export async function createAdminAccount(payload: CreateUserPayload): Promise<AdminUser> {
  return createUser(payload);
}

export async function updateAdminAccount(id: string, payload: UpdateUserPayload): Promise<AdminUser> {
  return updateUser(id, payload);
}

export async function deleteAdminAccount(id: string): Promise<void> {
  await deleteUser(id);
}

export async function listProviders(params: PaginationParams = {}): Promise<Paginated<ProviderProfile>> {
  const supabase = requireClient();
  const { rangeStart, rangeEnd, page } = buildPagination(params);
  let query = supabase
    .from<ProviderRow>('provider_profiles_view')
    .select('*', { count: 'exact' })
    .order('created_at', { ascending: false })
    .range(rangeStart, rangeEnd);

  if (params.search) {
    const term = `%${params.search}%`;
    query = query.or(`display_name.ilike.${term},contact_email.ilike.${term},description.ilike.${term}`);
  }
  if (params.status) {
    query = query.eq('status', params.status);
  }

  const { data, error, count } = await query;
  if (error) throw new Error(error.message);
  const results: ProviderProfile[] = (data ?? []).map((row) => ({
    id: row.id,
    user: row.user,
    display_name: row.display_name,
    contact_email: row.contact_email,
    phone_number: row.phone_number,
    website: row.website,
    description: row.description,
    address: row.address,
    status: row.status,
    reviewed_by: row.reviewed_by,
    reviewed_at: row.reviewed_at,
    created_at: row.created_at,
    updated_at: row.updated_at,
  }));

  const total = count ?? results.length;
  return {
    count: total,
    results,
    previous: page > 1 ? String(page - 1) : null,
    next: rangeEnd + 1 < total ? String(page + 1) : null,
  };
}

export async function createProvider(payload: Record<string, unknown>): Promise<ProviderProfile> {
  const supabase = requireClient();
  const reviewer = await getCurrentUserId();
  const insertPayload = {
    ...payload,
    reviewed_by: reviewer,
    reviewed_at: reviewer ? new Date().toISOString() : null,
  };
  const { data, error } = await supabase
    .from('provider_profiles')
    .insert(insertPayload)
    .select('*')
    .single();
  if (error || !data) throw new Error(error?.message ?? 'Failed to create provider.');
  return fetchProviderById(data.id);
}

export async function updateProvider(id: string, payload: Record<string, unknown>): Promise<ProviderProfile> {
  const supabase = requireClient();
  const { data, error } = await supabase
    .from('provider_profiles')
    .update(payload)
    .eq('id', id)
    .select('*')
    .single();
  if (error || !data) throw new Error(error?.message ?? 'Failed to update provider.');
  return fetchProviderById(data.id);
}

export async function deleteProvider(id: string): Promise<void> {
  const supabase = requireClient();
  const { error } = await supabase.from('provider_profiles').delete().eq('id', id);
  if (error) throw new Error(error.message);
}

export async function setProviderStatus(
  id: string,
  status: ProviderProfile['status'],
  notes?: string,
): Promise<ProviderProfile> {
  const supabase = requireClient();
  const reviewer = await getCurrentUserId();
  const payload: Record<string, unknown> = {
    status,
    reviewed_by: reviewer,
    reviewed_at: reviewer ? new Date().toISOString() : null,
  };
  if (notes !== undefined) payload.description = notes;
  const { data, error } = await supabase
    .from('provider_profiles')
    .update(payload)
    .eq('id', id)
    .select('*')
    .single();
  if (error || !data) throw new Error(error?.message ?? 'Failed to update provider status.');
  return fetchProviderById(data.id);
}

export async function listServices(params: PaginationParams = {}): Promise<Paginated<Service>> {
  const supabase = requireClient();
  const { rangeStart, rangeEnd, page } = buildPagination(params);
  let query = supabase
    .from<ServiceRow>('services_view')
    .select('*', { count: 'exact' })
    .order('updated_at', { ascending: false })
    .range(rangeStart, rangeEnd);

  if (params.search) {
    const term = `%${params.search}%`;
    query = query.or(`name.ilike.${term},summary.ilike.${term},description.ilike.${term}`);
  }
  if (params.status) {
    query = query.eq('status', params.status);
  }
  if (params.category) {
    query = query.eq('category_id', params.category);
  }

  const { data, error, count } = await query;
  if (error) throw new Error(error.message);
  const results: Service[] = (data ?? []).map((row) => ({
    id: row.id,
    name: row.name,
    slug: row.slug,
    summary: row.summary,
    description: row.description,
    status: row.status,
    approval_notes: row.approval_notes,
    provider_id: row.provider_id,
    category_id: row.category_id,
    provider: row.provider
      ? {
          id: row.provider.id,
          user: row.provider.user,
          display_name: row.provider.display_name,
          contact_email: row.provider.contact_email,
          phone_number: row.provider.phone_number,
          website: row.provider.website,
          description: row.provider.description,
          address: row.provider.address,
          status: row.provider.status,
          reviewed_by: row.provider.reviewed_by,
          reviewed_at: row.provider.reviewed_at,
          created_at: row.provider.created_at,
          updated_at: row.provider.updated_at,
        }
      : null,
    category: row.category,
    created_by: row.created_by,
    updated_by: row.updated_by,
    approved_by: row.approved_by,
    approved_at: row.approved_at,
    created_at: row.created_at,
    updated_at: row.updated_at,
  }));

  const total = count ?? results.length;
  return {
    count: total,
    results,
    previous: page > 1 ? String(page - 1) : null,
    next: rangeEnd + 1 < total ? String(page + 1) : null,
  };
}

export async function createService(payload: Record<string, unknown>): Promise<Service> {
  const supabase = requireClient();
  const actor = await getCurrentUserId();
  const insertPayload = {
    ...payload,
    created_by: actor,
    updated_by: actor,
  };
  const { data, error } = await supabase
    .from('services')
    .insert(insertPayload)
    .select('*')
    .single();
  if (error || !data) throw new Error(error?.message ?? 'Failed to create service.');
  return fetchServiceById(data.id);
}

export async function updateService(id: string, payload: Record<string, unknown>): Promise<Service> {
  const supabase = requireClient();
  const actor = await getCurrentUserId();
  const { data, error } = await supabase
    .from('services')
    .update({
      ...payload,
      updated_by: actor,
    })
    .eq('id', id)
    .select('*')
    .single();
  if (error || !data) throw new Error(error?.message ?? 'Failed to update service.');
  return fetchServiceById(data.id);
}

export async function deleteService(id: string): Promise<void> {
  const supabase = requireClient();
  const { error } = await supabase.from('services').delete().eq('id', id);
  if (error) throw new Error(error.message);
}

export async function setServiceStatus(
  id: string,
  status: Service['status'],
  approval_notes?: string,
): Promise<Service> {
  const supabase = requireClient();
  const actor = await getCurrentUserId();
  const now = new Date().toISOString();
  const { data, error } = await supabase
    .from('services')
    .update({
      status,
      approval_notes,
      approved_by: actor,
      approved_at: actor ? now : null,
    })
    .eq('id', id)
    .select('*')
    .single();
  if (error || !data) throw new Error(error?.message ?? 'Failed to update service status.');
  return fetchServiceById(data.id);
}

export async function listServiceCategories(): Promise<ServiceCategory[]> {
  const supabase = requireClient();
  const { data, error } = await supabase
    .from<ServiceCategory>('service_categories')
    .select('*')
    .order('name', { ascending: true });
  if (error) throw new Error(error.message);
  return data ?? [];
}

export async function createServiceCategory(payload: Record<string, unknown>): Promise<ServiceCategory> {
  const supabase = requireClient();
  const { data, error } = await supabase
    .from<ServiceCategory>('service_categories')
    .insert(payload)
    .select('*')
    .single();
  if (error || !data) throw new Error(error?.message ?? 'Failed to create service category.');
  return data;
}

export async function updateServiceCategory(id: string, payload: Record<string, unknown>): Promise<ServiceCategory> {
  const supabase = requireClient();
  const { data, error } = await supabase
    .from<ServiceCategory>('service_categories')
    .update(payload)
    .eq('id', id)
    .select('*')
    .single();
  if (error || !data) throw new Error(error?.message ?? 'Failed to update service category.');
  return data;
}

export async function deleteServiceCategory(id: string): Promise<void> {
  const supabase = requireClient();
  const { error } = await supabase.from('service_categories').delete().eq('id', id);
  if (error) throw new Error(error.message);
}
