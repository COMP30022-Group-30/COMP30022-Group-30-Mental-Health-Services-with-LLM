// cypress/e2e/home.smoke.cy.ts
describe('Home page smoke', () => {
  it('loads and shows primary navigation', () => {
    // Desktop width so nav items aren’t collapsed
    cy.viewport(1280, 900);

    cy.visit('/');

    // If there’s a cookie/consent banner in some environments, close it gently
    cy.get('body').then($b => {
      const btn = $b.find('[data-cy=cookie-accept], [data-testid=cookie-accept], button:contains("Accept")');
      if (btn.length) cy.wrap(btn.first()).click({ force: true });
    });

    // Wait for something we know should appear in the header
    cy.contains(/Support Atlas|Home|Chat|Help & Crisis|FAQ|Sign in/i, { timeout: 10000 })
      .should('be.visible');

    // If a hamburger exists on some breakpoints, open it so menu text becomes visible
    cy.get('body').then($b => {
      const burger = $b.find('[data-cy=nav-toggle], [aria-label="Toggle navigation"], button:contains("Menu")');
      if (burger.length) cy.wrap(burger.first()).click({ force: true });
    });

    // Assert at least one key nav/CTA is visible
    cy.contains(/Chat|Help & Crisis|FAQ|Sign in/i).should('be.visible');
  });
});


