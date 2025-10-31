describe('Offline / slow network UX', () => {
  it('shows offline banner and preserves input', () => {
    cy.intercept('GET', '**/mock/services.json', (req) => req.reply({ forceNetworkError: true })).as('services');

    cy.visit('/services');
    cy.wait('@services');

    cy.findByLabelText(/^search$/i).type('anxiety support');
    cy.findByRole('alert').should('contain.text', 'Failed to load services');
    cy.findByLabelText(/^search$/i).should('have.value', 'anxiety support');
  });
});
