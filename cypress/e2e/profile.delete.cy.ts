describe('Profile: delete account', () => {
  const baseUser = {
    id: 'user-1',
    email: 'user@example.com',
    name: 'Existing Name',
  };

  beforeEach(() => {
    cy.visit('/', {
      onBeforeLoad(win) {
        win.localStorage.setItem('sa_token', 'mock-token');
        win.localStorage.setItem('sa_user', JSON.stringify(baseUser));
      },
    });

    cy.intercept('GET', '**/auth/v1/user', {
      statusCode: 200,
      body: { user: {
        id: baseUser.id,
        email: baseUser.email,
        app_metadata: { provider: 'email', providers: ['email'] },
        user_metadata: { full_name: baseUser.name, avatar_url: null },
      } },
    }).as('getUser');

    cy.intercept('GET', '**/auth/v1/session*', {
      statusCode: 200,
      body: { data: { session: { user: {
        id: baseUser.id,
        email: baseUser.email,
        app_metadata: { provider: 'email', providers: ['email'] },
        user_metadata: { full_name: baseUser.name, avatar_url: null },
      } } }, error: null },
    }).as('getSession');

    cy.intercept('POST', '**/auth/v1/token?grant_type=refresh_token', {
      statusCode: 200,
      body: {
        access_token: 'mock-access-token',
        token_type: 'bearer',
        expires_in: 3600,
        refresh_token: 'mock-refresh-token',
        user: {
          id: baseUser.id,
          email: baseUser.email,
          app_metadata: { provider: 'email', providers: ['email'] },
          user_metadata: { full_name: baseUser.name, avatar_url: null },
        },
      },
    }).as('refreshToken');
  });

  it('removes the account when the backend succeeds', () => {
    cy.intercept('DELETE', '**/auth/v1/admin/users/**', {
      statusCode: 200,
      body: {},
    }).as('deleteUser');

    cy.intercept('POST', '**/auth/v1/logout', {
      statusCode: 200,
      body: {},
    }).as('logout');

    cy.on('window:confirm', () => true);

    cy.visit('/profile');

    cy.findByRole('button', { name: /delete account/i }).click();

    cy.wait('@deleteUser');
    cy.wait('@logout');

    cy.url().should('match', /\/?$/);
  });
});
