// frontend/web/src/test-utils.tsx
import { ReactElement, ReactNode } from 'react';
import { render as rtlRender, RenderOptions } from '@testing-library/react';
import { MemoryRouter, MemoryRouterProps } from 'react-router-dom';

import { AuthProvider } from './auth/AuthContext';
import type { User } from './auth/types';

// Extra providers from your admin & accessibility work
import { AdminAuthProvider } from './admin/AdminAuthContext';
import { DyslexicModeProvider } from './accessibility/DyslexicModeContext';
import { EasyModeProvider } from './accessibility/EasyModeContext';
import { HighContrastModeProvider } from './accessibility/HighContrastModeContext';
import { ScreenReaderModeProvider } from './accessibility/ScreenReaderModeContext';
import { LargeTextModeProvider } from './accessibility/LargeTextModeContext';
import { ReducedMotionModeProvider } from './accessibility/ReducedMotionModeContext';
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

  // Ensure accessibility preferences start disabled for predictable tests
  localStorage.removeItem('support-atlas:preferences:dyslexic-mode');
  localStorage.removeItem('support-atlas:preferences:easy-mode');
  localStorage.removeItem('support-atlas:preferences:high-contrast-mode');
  localStorage.removeItem('support-atlas:preferences:large-text-mode');
  localStorage.removeItem('support-atlas:preferences:reduced-motion-mode');
  localStorage.removeItem('support-atlas:preferences:screen-reader-mode');

  if (typeof document !== 'undefined') {
    const root = document.documentElement;
    ['data-dyslexic-mode', 'data-easy-mode', 'data-high-contrast', 'data-large-text', 'data-reduced-motion', 'data-screen-reader-assist'].forEach((attr) => {
      root.removeAttribute(attr);
    });
    ['dyslexic-mode', 'easy-mode', 'high-contrast-mode', 'large-text-mode', 'reduced-motion-mode', 'screen-reader-mode'].forEach((cls) => {
      root.classList.remove(cls);
    });
  }

  return (
    <ReducedMotionModeProvider>
      <ScreenReaderModeProvider>
        <HighContrastModeProvider>
          <LargeTextModeProvider>
            <EasyModeProvider>
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
            </EasyModeProvider>
          </LargeTextModeProvider>
        </HighContrastModeProvider>
      </ScreenReaderModeProvider>
    </ReducedMotionModeProvider>
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
