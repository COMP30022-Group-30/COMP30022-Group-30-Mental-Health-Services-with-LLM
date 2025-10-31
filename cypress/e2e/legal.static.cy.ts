// cypress/e2e/legal.static.cy.ts
describe('Legal & Crisis static pages', () => {
  it('footer links exist and open Terms/Privacy', () => {
    cy.visit('/');
    cy.findByRole('link', { name: /privacy/i }).should('have.attr', 'href').and('match', /privacy/);
    cy.findByRole('link', { name: /terms/i }).should('have.attr', 'href').and('match', /terms/);
  });

  it('crisis section on the home page mentions 000 and Lifeline', () => {
    cy.visit('/');
    cy.findByRole('link', { name: /see crisis contacts/i }).should('have.attr', 'href', '/#help-crisis');
    cy.get('#help-crisis').scrollIntoView().within(() => {
      cy.contains(/000/);
      cy.contains(/13 11 14/);
      cy.contains(/lifeline/i);
    });
  });
});
