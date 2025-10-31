const sampleServices = [
  {
    id: 'svc-3',
    name: 'Harbour Wellness Centre',
    suburb: 'Sydney',
    specialty: 'Group therapy',
    orgKind: 'private_clinic',
    createdAt: '2024-01-03T00:00:00Z',
    updatedAt: '2024-01-04T00:00:00Z',
  },
];

describe('Services search states', () => {
  it('shows empty state when no services match', () => {
    cy.mockServices([]);
    cy.visit('/services');
    cy.wait('@services');
    cy.contains('No results.').should('be.visible');
  });

  it('shows API error message', () => {
    cy.intercept('GET', '**/api/services*', (req) => req.reply({ forceNetworkError: true })).as('services');
    cy.visit('/services');
    cy.wait('@services');
    cy.findByRole('alert').should('contain.text', 'Failed to load services');
  });

  it('shows loading indicator during slow response', () => {
    cy.intercept('GET', '**/api/services*', (req) => {
      req.reply({ delay: 1200, body: sampleServices });
    }).as('services');

    cy.visit('/services');
    cy.get('section[aria-live="polite"]').should('have.attr', 'aria-busy', 'true');
    cy.wait('@services');
    cy.get('section[aria-live="polite"]').should('have.attr', 'aria-busy', 'false');
  });
});
