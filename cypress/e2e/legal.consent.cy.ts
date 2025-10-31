// cypress/e2e/legal.consent.cy.ts
describe('Consent before chat', () => {
  it('requires agreeing to terms and privacy before chatting', () => {
    cy.mockAgreements();
    cy.stubSupabaseAuth();
    cy.visit('/chat');

    cy.contains('h2', /terms/i).should('be.visible');
    cy.contains('button', /accept and continue/i).as('accept').should('be.disabled');

    cy.findByLabelText(/terms of service/i).click();
    cy.findByLabelText(/privacy policy/i).click();

    cy.get('@accept').should('not.be.disabled').click();
    cy.get('.chat-composer').should('be.visible');
  });

  it('Go back returns to the home page', () => {
    cy.mockAgreements();
    cy.stubSupabaseAuth();
    cy.visit('/chat');
    cy.contains('button', /go back/i).click();
    cy.location('pathname').should('eq', '/');
  });
});
