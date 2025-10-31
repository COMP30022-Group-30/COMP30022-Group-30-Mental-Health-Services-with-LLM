// cypress/e2e/a11y.responsive.cy.ts
describe('Responsive layout', () => {
  const sizes: Cypress.ViewportPreset[] = ['iphone-6', 'ipad-2', 'macbook-15'];

  sizes.forEach((vp) => {
    it(`shows key controls on ${vp}`, () => {
      cy.viewport(vp);
      cy.visit('/');

      cy.findByRole('link', { name: /support atlas home/i }).should('be.visible');
      cy.findByRole('complementary', { name: /quick exit banner/i }).should('be.visible');
      cy.findByRole('button', { name: /start chat/i }).should('be.visible');
    });
  });
});
