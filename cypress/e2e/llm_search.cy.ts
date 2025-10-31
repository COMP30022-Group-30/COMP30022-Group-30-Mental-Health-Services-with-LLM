describe('LLM search smoke', () => {
  const acceptConsent = () => {
    cy.contains('button', /accept and continue/i).as('accept').should('be.disabled');
    cy.findByLabelText(/terms of service/i).click();
    cy.findByLabelText(/privacy policy/i).click();
    cy.get('@accept').click();
  };

  it('accepts a chat query and renders assistant guidance', () => {
    cy.intercept('POST', '**/api/v1/chat/chat**', {
      statusCode: 200,
      body: {
        response: 'Here are a few local services you can explore.',
        session_id: 'session-search',
      },
    }).as('chat');

    cy.visit('/chat');
    cy.mockAgreements();
    acceptConsent();

    cy.get('#chat-composer-input').type('What mental-health support is nearby?');
    cy.findByRole('button', { name: /send/i }).click();

    cy.wait('@chat');
    cy.get('.msg.assistant .msg-text').contains(/local services/i).should('be.visible');
  });
});
