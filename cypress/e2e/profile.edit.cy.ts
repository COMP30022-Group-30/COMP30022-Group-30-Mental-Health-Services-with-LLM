describe('Profile: edit', () => {
  const baseUser = {
    id: 'user-1',
    email: 'user@example.com',
    name: 'Existing Name',
  };

  const supabaseUser = {
    id: baseUser.id,
    email: baseUser.email,
    app_metadata: { provider: 'email', providers: ['email'] },
    user_metadata: { full_name: baseUser.name, avatar_url: null },
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
      body: { user: supabaseUser },
    }).as('getUser');

    cy.intercept('GET', '**/auth/v1/session*', {
      statusCode: 200,
      body: { data: { session: { user: supabaseUser } }, error: null },
    }).as('getSession');

    cy.intercept('POST', '**/auth/v1/token?grant_type=refresh_token', {
      statusCode: 200,
      body: {
        access_token: 'mock-access-token',
        token_type: 'bearer',
        expires_in: 3600,
        refresh_token: 'mock-refresh-token',
        user: supabaseUser,
      },
    }).as('refreshToken');
  });

  it('updates the display name when the backend succeeds', () => {
    cy.intercept('PUT', '**/auth/v1/user', (req) => {
      expect(req.body).to.have.nested.property('data.full_name', 'Updated Name');
      req.reply({
        statusCode: 200,
        body: {
          user: {
            ...supabaseUser,
            user_metadata: { full_name: 'Updated Name', avatar_url: null },
          },
        },
      });
    }).as('updateUser');

    cy.visit('/profile');

    cy.findByLabelText(/display name/i).clear().type('Updated Name');
    cy.findByRole('button', { name: /save changes/i }).click();

    cy.wait('@updateUser');
    cy.findByRole('status').should('contain.text', 'Account details updated');
  });
});
