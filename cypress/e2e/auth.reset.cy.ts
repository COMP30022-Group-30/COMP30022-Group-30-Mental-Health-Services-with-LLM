describe('Auth: password reset', () => {
  it('requests a reset link via the login page', () => {
    cy.stubSupabaseAuth();
    cy.intercept('POST', /\/auth\/v1\/recover.*/, { statusCode: 200, body: {} }).as('supabaseRecover');

    cy.visit('/login');
    cy.contains('button', /forgot password/i).click();

    cy.findByLabelText(/email/i).type('user@example.com');
    cy.findByRole('button', { name: /email me a reset link/i }).click();

    cy.wait('@supabaseRecover');
    cy.contains(/check your inbox/i).should('be.visible');
  });

  it('shows guidance when arriving without a valid session', () => {
    cy.stubSupabaseAuth();
    cy.visit('/reset-password');
    cy.contains(/this password reset link is invalid or has expired/i).should('be.visible');
  });
});
