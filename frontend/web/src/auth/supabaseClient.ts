import { createClient, type SupabaseClient } from '@supabase/supabase-js';
import { VITE } from '@/utils/env';

let supabase: SupabaseClient | null = null;

export function getSupabaseClient(): SupabaseClient | null {
  if (supabase) return supabase;

  const url = VITE.VITE_SUPABASE_URL;
  const anonKey = VITE.VITE_SUPABASE_ANON_KEY;

  if (!url || !anonKey) {
    if (typeof window !== 'undefined') {
      const mock = (window as typeof window & { __SUPABASE_TEST_CLIENT__?: SupabaseClient }).__SUPABASE_TEST_CLIENT__;
      if (mock) {
        supabase = mock;
        return supabase;
      }
    }
    return null;
  }

  supabase = createClient(url, anonKey, {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true,
    },
  });

  return supabase;
}
