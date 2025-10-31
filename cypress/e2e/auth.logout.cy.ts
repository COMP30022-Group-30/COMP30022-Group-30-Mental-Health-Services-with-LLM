describe('Auth: logout', () => {
  it('clears session and shows sign-in CTA', () => {
    cy.stubSupabaseAuth();
    cy.visit('/login');
    cy.findByLabelText(/email/i).type('user@example.com');
    cy.findByLabelText(/password/i).type('StrongP@ss1');
    cy.findByRole('button', { name: /sign in with email/i }).click();
    cy.wait('@supabasePassword');

    cy.location('pathname').should('eq', '/');
    cy.findByRole('button', { name: /sign out/i }).click();

    cy.wait('@supabaseLogout');
    cy.findByRole('link', { name: /sign in/i }).should('be.visible');
  });
});
