describe('Home page smoke', () => {
  it('loads and shows primary nav/cta', () => {
    // Wider viewport so top-nav items aren’t hidden
    cy.viewport(1280, 900);
    cy.visit('/');

    // (Optional) close cookie/consent if present
    cy.get('body').then($b => {
      const consentBtn = $b.find('[data-cy=cookie-accept], [data-testid=cookie-accept], button:contains("Accept")');
      if (consentBtn.length) cy.wrap(consentBtn.first()).click({ force: true });
    });

    // Wait for the app shell to render (brand or header)
    // Prefer a stable hook if you add one: [data-cy=app-header]
    cy.contains(/Support Atlas|Help & Crisis|Chat|Sign in/i, { timeout: 10000 })
      .should('be.visible');

    // If a hamburger is used on small screens, open it and assert nav items
    cy.get('body').then($b => {
      const burger = $b.find('[data-cy=nav-toggle], [aria-label="Toggle navigation"], button:contains("Menu")');
      if (burger.length) cy.wrap(burger.first()).click();
    });

    // Assert at least one key nav item is visible
    cy.contains(/Chat|Help & Crisis|FAQ|Sign in/i).should('be.visible');
  });
});

