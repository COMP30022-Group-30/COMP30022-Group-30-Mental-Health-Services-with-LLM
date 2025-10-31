describe('Keyboard navigation', () => {
  it('tabs through skip link, quick exit, and chat CTA', () => {
    cy.visit('/');

    cy.realPress('Tab');
    cy.focused()
      .should('have.class', 'quick-exit-button')
      .and('have.attr', 'aria-label')
      .and('match', /quick exit/i);

    cy.realPress('Tab');
    cy.focused()
      .should('have.class', 'skip-link')
      .and('have.attr', 'href', '#main');

    cy.realPress('Tab');
    cy.focused()
      .should('have.attr', 'type', 'button')
      .and('contain.text', 'Start chat');
  });
});
