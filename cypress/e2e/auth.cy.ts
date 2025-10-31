describe('Auth flow (stubbed)', () => {
  it('signs in with email/password and persists session across reload', () => {
    cy.stubSupabaseAuth();
    cy.visit('/login');

    cy.findByLabelText(/email/i).type('user@example.com');
    cy.findByLabelText(/password/i).type('StrongP@ss1');
    cy.findByRole('button', { name: /sign in with email/i }).click();

    cy.location('pathname').should('eq', '/');
    cy.findByRole('button', { name: /sign out/i }).should('be.visible');

    cy.reload();
    cy.findByRole('button', { name: /sign out/i }).should('be.visible');
  });
});
