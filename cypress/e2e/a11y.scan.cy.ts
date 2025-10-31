describe('A11y scan', () => {
  it('home has no serious violations', () => {
    cy.visit('/');
    cy.injectAxe();
    cy.checkA11y(null, { includedImpacts: ['serious', 'critical'] });
  });

  it('services directory has no serious violations', () => {
    cy.mockServices([]);
    cy.visit('/services');
    cy.wait('@services');
    cy.injectAxe();
    cy.checkA11y(null, { includedImpacts: ['serious', 'critical'] });
  });
});
