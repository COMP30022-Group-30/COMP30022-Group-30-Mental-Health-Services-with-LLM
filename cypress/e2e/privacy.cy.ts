// cypress/e2e/privacy.cy.ts
describe('Privacy hygiene', () => {
  it('does not leak directory search terms into the URL', () => {
    cy.mockServices([{ id: 'svc-1', name: 'Calm Minds Clinic', suburb: 'Melbourne', specialty: 'Counselling', orgKind: 'private_clinic', createdAt: '2024-01-01T00:00:00Z' }]);
    cy.visit('/services');
    cy.wait('@services');

    cy.findByLabelText(/^search$/i).type('counselling services near me');
    cy.location('search').should('eq', '');
  });

  it('stores preferences under expected keys only', () => {
    cy.visit('/accessibility');
    cy.window().then((win) => {
      const keys: string[] = [];
      for (let i = 0; i < win.localStorage.length; i += 1) {
        const key = win.localStorage.key(i);
        if (key) keys.push(key);
      }
      expect(keys.filter((k) => k.startsWith('support-atlas:preferences:')).length).to.be.greaterThan(0);
      expect(keys.find((k) => /chat|message|history/i.test(k))).to.be.undefined;
    });
  });
});
