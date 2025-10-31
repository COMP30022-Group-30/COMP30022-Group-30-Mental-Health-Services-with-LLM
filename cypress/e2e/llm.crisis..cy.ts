describe('LLM crisis guardrail flow', () => {
  const acceptConsent = () => {
    cy.contains('button', /accept and continue/i).as('accept').should('be.disabled');
    cy.findByLabelText(/terms of service/i).click();
    cy.findByLabelText(/privacy policy/i).click();
    cy.get('@accept').click();
  };

  it('shows crisis banner and blocks unsafe suggestions for self-harm prompts', () => {
    cy.intercept({ method: 'POST', url: /\\/api\\/v1\\/chat\\/chat\\/?(?:\\?.*)?$/ }, {
      statusCode: 200,
      body: {
        response: 'If you are in immediate danger please call 000 or Lifeline on 13 11 14.',
        session_id: 'session-crisis',
        action: 'crisis_halt',
        resources: [{ label: 'Call Lifeline', href: 'tel:131114' }],
      },
    }).as('chat');

    cy.mockAgreements();
    cy.visit('/chat');
    acceptConsent();

    cy.get('#chat-composer-input').type('I want to end it all');
    cy.findByRole('button', { name: /send/i }).click();

    cy.wait('@chat');

    cy.get('.chat-alert.crisis').should('be.visible').within(() => {
      cy.contains(/immediate danger/i);
      cy.contains(/000/);
      cy.contains(/13 11 14/);
      cy.findByRole('link', { name: /call lifeline/i }).should('have.attr', 'href', 'tel:131114');
    });
  });
});
