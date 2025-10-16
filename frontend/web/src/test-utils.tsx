// frontend/web/src/test-utils.tsx
import { ReactElement, ReactNode } from 'react';
import { render as rtlRender, RenderOptions } from '@testing-library/react';
import { MemoryRouter, MemoryRouterProps } from 'react-router-dom';

import { AuthProvider } from './auth/AuthContext';
import type { User } from './auth/types';

// Extra providers from your admin & accessibility work
import { AdminAuthProvider } from './admin/AdminAuthContext';
import { DyslexicModeProvider } from './accessibility/DyslexicModeContext';
import type { AdminUser } from './types/admin';

type ProvidersProps = {
  children: ReactNode;
  router?: Partial<MemoryRouterProps>;
  /** If you pass a user, we simulate logged-in state via localStorage */
  auth?: { user?: User | { id: string; name: string } | null };
  /** Optional admin context seed */
  admin?: { admin?: AdminUser | null; loading?: boolean; error?: string | null };
};

export function Providers({ children, router, auth, admin }: ProvidersProps) {
  const initialEntries = router?.initialEntries ?? ['/'];

  // Seed localStorage so AuthProvider hydrates
  if (auth?.user) {
    localStorage.setItem('sa_token', 'test-token');
    localStorage.setItem('sa_user', JSON.stringify(auth.user));
  } else {
    localStorage.removeItem('sa_token');
    localStorage.removeItem('sa_user');
  }

  // Ensure dyslexic-mode starts disabled for predictable tests
  localStorage.removeItem('support-atlas:preferences:dyslexic-mode');

  return (
    <DyslexicModeProvider>
      <AuthProvider>
        <AdminAuthProvider
          hydrateOnMount={false}
          initialState={admin ?? { admin: null, loading: false, error: null }}
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