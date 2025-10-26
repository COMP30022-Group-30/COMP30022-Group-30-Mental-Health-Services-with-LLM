describe('Home page smoke', () => {
  it('loads and shows primary navigation', () => {
    cy.viewport(1280, 900);          // avoid mobile-collapsed nav
    cy.visit('/');

    // Wait for any obvious header/nav text that exists on your site
    cy.contains(/Support Atlas|Home|Chat|Help & Crisis|FAQ|Sign in/i, { timeout: 10000 })
      .should('be.visible');

    // If a hamburger exists at some breakpoints, open it
    cy.get('body').then($b => {
      const burger = $b.find('[data-cy=nav-toggle], [aria-label="Toggle navigation"], button:contains("Menu")');
      if (burger.length) cy.wrap(burger.first()).click({ force: true });
    });

    // Assert at least one key nav link/CTA
    cy.contains(/Chat|Help & Crisis|FAQ|Sign in/i).should('be.visible');
  });
});

