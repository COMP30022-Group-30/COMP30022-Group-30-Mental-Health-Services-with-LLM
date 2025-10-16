import userEvent from '@testing-library/user-event';
import { it, expect, beforeEach } from 'vitest';
import App from '@/App';
import { render, screen, waitFor } from '@testing-library/react';
import { Providers } from '@/test-utils';

beforeEach(() => {
  localStorage.removeItem('support-atlas:preferences:dyslexic-mode');
  document.documentElement.removeAttribute('data-dyslexic-mode');
  document.documentElement.classList.remove('dyslexic-mode');
});

it('enables and disables dyslexia-friendly mode', async () => {
  const user = userEvent.setup();
  render(
    <Providers router={{ initialEntries: ['/accessibility'] }}>
      <App />
    </Providers>
  );

  const toggle = await screen.findByRole('button', { name: /dyslexia-friendly mode/i });

  expect(toggle).toHaveAttribute('aria-pressed', 'false');
  expect(document.documentElement.getAttribute('data-dyslexic-mode')).toBe('off');

  await user.click(toggle);

  await waitFor(() => {
    expect(toggle).toHaveAttribute('aria-pressed', 'true');
    expect(document.documentElement.getAttribute('data-dyslexic-mode')).toBe('on');
  });

  await user.click(toggle);

  await waitFor(() => {
    expect(toggle).toHaveAttribute('aria-pressed', 'false');
    expect(document.documentElement.getAttribute('data-dyslexic-mode')).toBe('off');
  });
});
