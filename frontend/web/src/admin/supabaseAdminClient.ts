import { createClient, type SupabaseClient } from '@supabase/supabase-js';
import { VITE } from '@/utils/env';

let adminClient: SupabaseClient | null = null;

export function getSupabaseAdminClient(): SupabaseClient | null {
  if (adminClient) return adminClient;

  const url = VITE.VITE_SUPABASE_URL;
  const serviceKey = VITE.VITE_SUPABASE_SERVICE_KEY;

  if (!url || !serviceKey) {
    if (typeof window !== 'undefined') {
      const mock = (window as typeof window & { __SUPABASE_TEST_ADMIN_CLIENT__?: SupabaseClient }).__SUPABASE_TEST_ADMIN_CLIENT__;
      if (mock) {
        adminClient = mock;
        return adminClient;
      }
    }
    return null;
  }

  adminClient = createClient(url, serviceKey, {
    auth: {
      persistSession: false,
      autoRefreshToken: false,
    },
  });

  return adminClient;
}
