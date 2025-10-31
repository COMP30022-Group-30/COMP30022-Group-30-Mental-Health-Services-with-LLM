describe('Auth: role-based access', () => {
  it('redirects unauthenticated users to the admin sign-in page', () => {
    cy.visit('/admin');
    cy.location('pathname').should('eq', '/admin/signin');
  });

  it('shows the admin sign-in form', () => {
    cy.visit('/admin/signin');
    cy.findByLabelText(/username/i).should('exist');
    cy.findByLabelText(/password/i).should('exist');
  });
});
