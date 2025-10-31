const mockUser = {
  id: 'user-1',
  email: 'user@example.com',
  app_metadata: { provider: 'email', providers: ['email'] },
  user_metadata: { full_name: 'Mock User' },
  aud: 'authenticated' as const,
  role: 'authenticated',
  created_at: '2024-01-01T00:00:00.000Z',
  updated_at: '2024-01-01T00:00:00.000Z',
};

function buildSession() {
  const expiresIn = 3600;
  const expiresAt = Math.floor(Date.now() / 1000) + expiresIn;
  const accessToken = 'mock-access-token';
  const refreshToken = 'mock-refresh-token';

  return {
    access_token: accessToken,
    token_type: 'bearer',
    expires_in: expiresIn,
    refresh_token: refreshToken,
    expires_at: expiresAt,
    user: mockUser,
    session: {
      access_token: accessToken,
      token_type: 'bearer',
      expires_in: expiresIn,
      refresh_token: refreshToken,
      expires_at: expiresAt,
      user: mockUser,
    },
  };
}

declare global {
  namespace Cypress {
    interface Chainable {
      stubSupabaseAuth(): Chainable<void>;
      mockServices(body?: unknown[]): Chainable<void>;
      mockAnalytics(callback?: (body: any) => void): Chainable<void>;
      mockAgreements(status?: {
        requiresAcceptance?: boolean;
        termsAccepted?: boolean;
        privacyAccepted?: boolean;
      }): Chainable<void>;
      seedUserSession(): Chainable<void>;
    }
  }
}

Cypress.Commands.add('stubSupabaseAuth', () => {
  const session = buildSession();

  cy.intercept('POST', /\/auth\/v1\/token\?grant_type=password/, (req) => {
    req.reply({ statusCode: 200, body: session });
  }).as('supabasePassword');

  cy.intercept('POST', /\/auth\/v1\/token\?grant_type=refresh_token/, (req) => {
    req.reply({ statusCode: 200, body: session });
  }).as('supabaseRefresh');

  cy.intercept('POST', /\/auth\/v1\/otp/, { statusCode: 200, body: { message: 'Email sent' } }).as('supabaseOtp');

  cy.intercept('POST', /\/auth\/v1\/verify/, (req) => {
    req.reply({ statusCode: 200, body: session });
  }).as('supabaseVerify');

  cy.intercept('POST', /\/auth\/v1\/logout/, { statusCode: 200, body: {} }).as('supabaseLogout');

  cy.intercept('GET', /\/auth\/v1\/user/, { statusCode: 200, body: { user: mockUser } }).as('supabaseGetUser');

  cy.intercept('GET', /\/rest\/v1\/legal_acceptances.*/, (req) => {
    req.reply({ statusCode: 200, body: [] });
  }).as('supabaseLegalFetch');

  cy.intercept('POST', /\/rest\/v1\/legal_acceptances.*/, { statusCode: 200, body: {} }).as('supabaseLegalUpsert');
});

Cypress.Commands.add('mockServices', (body: unknown[] = []) => {
  cy.intercept('GET', '**/mock/services.json', (req) => {
    req.reply({ statusCode: 200, body });
  }).as('services');

  cy.intercept('GET', '**/api/services*', (req) => {
    req.reply({ statusCode: 200, body });
  });
});

Cypress.Commands.add('mockAnalytics', (callback?: (body: any) => void) => {
  cy.intercept('POST', '**/api/analytics/events', (req) => {
    callback?.(req.body);
    req.reply({ statusCode: 204, body: '' });
  }).as('analytics');
});

Cypress.Commands.add('mockAgreements', (status = {}) => {
  const baseStatus = {
    termsVersion: '2025-02-17',
    privacyVersion: '2025-02-17',
    termsAccepted: false,
    privacyAccepted: false,
    requiresAcceptance: true,
    ...status,
  };

  const respond = { statusCode: 200, body: baseStatus };

  cy.intercept('GET', '**/rest/v1/legal_acceptances*', (req) => {
    req.reply(respond);
  }).as('agreementsFetch');

  cy.intercept('POST', '**/rest/v1/legal_acceptances*', (req) => {
    req.reply({
      statusCode: 200,
      body: { ...baseStatus, termsAccepted: true, privacyAccepted: true, requiresAcceptance: false },
    });
  }).as('agreementsSave');

  cy.intercept('GET', '**/api/v1/chat/agreements/status*', respond).as('agreementsStatus');
  cy.intercept('POST', '**/api/v1/chat/agreements/accept*', {
    statusCode: 200,
    body: { ...baseStatus, termsAccepted: true, privacyAccepted: true, requiresAcceptance: false },
  }).as('agreementsAccept');
});

Cypress.Commands.add('seedUserSession', () => {
  const user = {
    id: 'user-1',
    email: 'user@example.com',
    name: 'Mock User',
  };

  cy.visit('/', {
    onBeforeLoad(win) {
      win.localStorage.setItem('sa_token', 'mock-token');
      win.localStorage.setItem('sa_user', JSON.stringify(user));
    },
  });
});

export {};
