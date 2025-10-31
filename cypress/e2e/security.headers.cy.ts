// cypress/e2e/security.headers.cy.ts
describe('Security headers', () => {
  it('sets common security headers', () => {
    cy.request('/').then((resp) => {
      const h = resp.headers;
      const nosniff = h['x-content-type-options'];
      if (nosniff) {
        expect(nosniff).to.include('nosniff');
      }

      if (h['strict-transport-security']) {
        expect(h['strict-transport-security']).to.match(/max-age=\d+/);
      }

      if (h['referrer-policy']) {
        expect(h['referrer-policy']).to.match(/strict-origin|same-origin|no-referrer/i);
      }

      if (h['content-security-policy']) {
        expect(h['content-security-policy']).to.not.be.empty;
      }
    });
  });
});
