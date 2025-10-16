import { useMemo } from 'react';
import { NavLink } from 'react-router-dom';
import Container from './Container';
import { useAuth } from '@/auth/AuthContext';
import { useScreenReaderMode } from '@/accessibility/ScreenReaderModeContext';

export default function Header() {
  const { user, loading, signOut } = useAuth();
  const { screenReaderAssist } = useScreenReaderMode();

  const initials = useMemo(() => {
    const source = user?.name ?? user?.email ?? '';
    if (!source) return 'U';
    const parts = source
      .trim()
      .split(/\s+/)
      .map((part) => part.charAt(0))
      .filter(Boolean)
      .slice(0, 2);
    return parts.length ? parts.join('').toUpperCase() : source.charAt(0).toUpperCase();
  }, [user?.name, user?.email]);

  const handleSignOut = () => {
    if (signOut) {
      void signOut();
    }
  };

  return (
    <header className="header">
      <Container>
        <a href="#main" className="skip-link">Skip to main content</a>
        <div className="header-inner">
          <a href="/" className="brand" aria-label="Support Atlas home">
            <span aria-hidden className="logo">SA</span>
            <span className="brand-name">Support Atlas</span>
          </a>

          <div className="header-right">
            {screenReaderAssist && (
              <p className="sr-only" aria-live="polite">
                Screen reader assist mode is on. Use the skip link and landmarks to jump between sections.
              </p>
            )}
            <nav
              className="nav"
              aria-label={screenReaderAssist ? 'Primary navigation — Support Atlas main sections' : 'Primary'}
            >
              <NavLink to="/" end className={({ isActive }) => (isActive ? 'active' : undefined)}>
                Home
              </NavLink>
              <NavLink
                to="/chat"
                data-easy-mode="priority"
                className={({ isActive }) => (isActive ? 'active' : undefined)}
              >
                Chat
              </NavLink>
              {/* Removed Services; add in-page anchors for Help & Crisis and FAQ */}
              <a href="/#help-crisis" data-easy-mode="priority">Help &amp; Crisis</a>
              <a href="/#faq" data-easy-mode="hide">FAQ</a>
            </nav>

            <NavLink
              to="/accessibility"
              className={({ isActive }) => (isActive ? 'accessibility-trigger active' : 'accessibility-trigger')}
            >
              <span className="accessibility-trigger-label">Accessibility</span>
            </NavLink>

            <div className="auth-actions" aria-label="Account actions">
              {loading ? (
                <span className="auth-status" aria-live="polite">Loading…</span>
              ) : user ? (
                <>
                  <NavLink
                    to="/profile"
                    className={({ isActive }) => (isActive ? 'profile-chip active' : 'profile-chip')}
                  >
                    <span className="profile-chip-avatar" aria-hidden>
                      {user.avatarUrl ? <img src={user.avatarUrl} alt="" /> : initials}
                    </span>
                    <span className="profile-chip-label">
                      <strong>{user.name ?? user.email ?? 'Profile'}</strong>
                      {user.name && user.email && (
                        <small data-easy-mode="hide">{user.email}</small>
                      )}
                    </span>
                  </NavLink>
                  <button type="button" className="btn btn-link auth-signout" onClick={handleSignOut}>
                    Sign out
                  </button>
                </>
              ) : (
                <NavLink to="/login" className="btn btn-secondary">
                  Sign in
                </NavLink>
              )}
            </div>
          </div>
        </div>
      </Container>
    </header>
  );
}
