const servicesFixture = [
  {
    id: 'svc-1',
    name: 'Calm Minds Clinic',
    suburb: 'Melbourne',
    specialty: 'Counselling',
    orgKind: 'private_clinic',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-05T00:00:00Z',
  },
  {
    id: 'svc-2',
    name: 'Cityview Hospital',
    suburb: 'Sydney',
    specialty: 'Inpatient care',
    orgKind: 'hospital',
    createdAt: '2024-01-02T00:00:00Z',
    updatedAt: '2024-01-06T00:00:00Z',
  },
];

describe('Search with filters', () => {
  beforeEach(() => {
    cy.mockServices(servicesFixture);
    cy.visit('/services');
    cy.wait('@services');
  });

  it('filters by keyword and type', () => {
    cy.findByLabelText(/^search$/i).type('calm');
    cy.contains('.card', 'Calm Minds Clinic').should('be.visible');
    cy.contains('.card', 'Cityview Hospital').should('not.exist');
    cy.contains('#results-summary', /1 result/i);

    cy.findByLabelText(/^search$/i).clear();
    cy.findByLabelText(/type/i).select('Hospital');
    cy.contains('.card', 'Cityview Hospital').should('be.visible');
    cy.contains('.card', 'Calm Minds Clinic').should('not.exist');
    cy.contains('#results-summary', /1 result/i);
  });
});
