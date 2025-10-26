// LLM search smoke — must render EXACTLY ONE of: clinics OR helplines

describe('LLM search (smoke)', () => {
  it('accepts a query and renders clinics XOR helplines', () => {
    // ✅ Go straight to the live chat page (baseUrl will be production)
    cy.visit('/chat');

    const inputSel = '[data-cy=search-input]';
    const submitSel = '[data-cy=search-submit]';

    // ✅ Intercept the real LLM request (your CloudFront endpoint)
    cy.intercept('POST', '**cloudfront.net/api/v1/chat/chat*').as('llm');

    // Type + submit (supports hooks or visible fallback)
    cy.get('body').then($b => {
      const hasHook = $b.find(inputSel).length > 0;
      const input = hasHook
        ? cy.get(inputSel).should('be.visible')
        : cy.get('input, textarea').filter(':visible').first();

      input.type('anxiety support{enter}');
      if ($b.find(submitSel).length) cy.get(submitSel).click();
    });

    // Wait for LLM and ensure it returned 2xx
    cy.wait('@llm', { timeout: 30000 })
      .its('response.statusCode')
      .should('be.within', 200, 299);

    // XOR: exactly one of clinics OR helplines should be present
    cy.get('body').should($b => {
      const hasClinicsHook = $b.find('[data-cy=results-clinics]').length > 0;
      const hasHelplinesHook = $b.find('[data-cy=results-helplines]').length > 0;

      const text = $b.text();
      const clinicsText = /(The Melbourne Clinic|University of Melbourne Psychology Clinic|Aspect Clinic|Location:|Contact:)/i.test(text);
      const helplinesText = /(Lifeline|Beyond Blue|Suicide Call Back Service|13\s?11\s?14|1300\s?22\s?4636|1300\s?659\s?467)/i.test(text);

      const clinics = hasClinicsHook || clinicsText;
      const helplines = hasHelplinesHook || helplinesText;

      const xor = (a: boolean, b: boolean) => (a && !b) || (!a && b);
      expect(xor(clinics, helplines), 'exactly one of clinics or helplines rendered').to.be.true;
    });
  });
});
