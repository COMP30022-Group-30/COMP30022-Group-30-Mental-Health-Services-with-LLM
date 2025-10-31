describe('Auth: email/password signup', () => {
  beforeEach(() => {
    cy.stubSupabaseAuth();
    cy.visit('/login');
  });

  it('creates an account with valid fields', () => {
    cy.contains('button', /create an email account/i).click();

    cy.findByLabelText(/email/i).type('new.user@example.com');
    cy.findByLabelText(/password/i).type('StrongP@ss12');
    cy.findByLabelText(/confirm password/i).type('StrongP@ss12');
    cy.findByRole('button', { name: /create account/i }).click();

    cy.location('pathname').should('eq', '/');
    cy.findByRole('button', { name: /sign out/i }).should('be.visible');
  });

  it('shows inline errors on invalid input', () => {
    cy.contains('button', /create an email account/i).click();
    cy.findByRole('button', { name: /create account/i }).click();
    cy.findAllByText(/required|must be at least 6 characters|do not match/i).should('exist');
  });
});
