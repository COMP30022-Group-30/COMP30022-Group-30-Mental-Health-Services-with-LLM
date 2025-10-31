describe('Services page smoke', () => {
  it('renders filters and results area', () => {
    cy.mockServices([]);
    cy.visit('/services');
    cy.wait('@services');

    cy.findByRole('heading', { name: /all services/i }).should('be.visible');
    cy.findByLabelText(/^search$/i).should('exist');
    cy.findByRole('complementary', { name: /filters/i }).should('exist');
    cy.get('section[aria-live="polite"]').should('have.attr', 'aria-busy', 'false');
  });
});
