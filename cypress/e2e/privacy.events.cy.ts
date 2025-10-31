describe('Privacy: analytics/events guard', () => {
  it('ensures analytics payload is anonymised', () => {
    cy.mockAnalytics((body) => {
      expect(body).to.have.keys(['event', 'anonId', 'ts']);
      expect(body).not.to.have.any.keys('email', 'name', 'message', 'chat');
    });

    cy.visit('/');
    cy.findByRole('button', { name: /start chat/i }).click();

    cy.wait('@analytics');
  });
});
