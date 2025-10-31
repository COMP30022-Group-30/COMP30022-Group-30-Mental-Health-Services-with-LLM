describe('Auth: OAuth buttons (mocked)', () => {
  ['google', 'github'].forEach((provider) => {
    it(`logs in with ${provider}`, () => {
      cy.stubSupabaseAuth();
      cy.visit('/login');
      cy.findByRole('button', { name: new RegExp(provider, 'i') }).click();

      cy.location('pathname').should('eq', '/');
      cy.findByRole('button', { name: /sign out/i }).should('be.visible');
    });
  });
});
