import { ReactElement, ReactNode } from 'react';
import { render as rtlRender, RenderOptions } from '@testing-library/react';
import { MemoryRouter, MemoryRouterProps } from 'react-router-dom';
import { AuthProvider } from './auth/AuthContext';
import { AdminAuthProvider } from './admin/AdminAuthContext';
import { DyslexicModeProvider } from './accessibility/DyslexicModeContext';
import type { User } from './auth/types';
import type { AdminUser } from './types/admin';

type TestUser = User | { id: string; name?: string; email?: string; avatarUrl?: string };

type ProvidersProps = {
  children: ReactNode;
  router?: Partial<MemoryRouterProps>;
  /** If you pass a user, we simulate logged-in state via localStorage */
  auth?: { user?: TestUser | null; loading?: boolean };
  admin?: { admin?: AdminUser | null; loading?: boolean; error?: string | null };
};

/**
 * Test wrapper that provides:
 *  - MemoryRouter (so you can set initialEntries)
 *  - AuthProvider (so useAuth() works)
 *  - Optional "logged-in" state by seeding localStorage keys
 */
export function Providers({ children, router, auth, admin }: ProvidersProps) {
  const initialEntries = router?.initialEntries ?? ['/'];

  const authUser = auth?.user ? ({ ...auth.user } as User) : null;
  const authInitialState = {
    user: authUser,
    loading: auth?.loading ?? false,
  };
  const adminInitialState = admin ?? { admin: null, loading: false, error: null };

  // Normalise auth state into storage so AuthProvider picks it up
  if (authUser) {
    localStorage.setItem('sa_token', 'test-token');
    localStorage.setItem('sa_user', JSON.stringify(authUser));
  } else {
    localStorage.removeItem('sa_token');
    localStorage.removeItem('sa_user');
  }
  localStorage.removeItem('support-atlas:preferences:dyslexic-mode');

  return (
    <DyslexicModeProvider>
      <AuthProvider initialState={authInitialState}>
        <AdminAuthProvider
          hydrateOnMount={false}
          initialState={adminInitialState}
        >
          <MemoryRouter initialEntries={initialEntries}>{children}</MemoryRouter>
        </AdminAuthProvider>
      </AuthProvider>
    </DyslexicModeProvider>
  );
}

type CustomRenderOptions = RenderOptions & Omit<ProvidersProps, 'children'>;

export function render(
  ui: ReactElement,
  { router, auth, admin, ...renderOptions }: CustomRenderOptions = {},
) {
  return rtlRender(
    <Providers router={router} auth={auth} admin={admin}>
      {ui}
    </Providers>,
    renderOptions,
  );
}

export * from '@testing-library/react';
