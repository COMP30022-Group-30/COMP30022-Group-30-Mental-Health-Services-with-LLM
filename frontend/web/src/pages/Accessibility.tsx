import DyslexicModeToggle from '@/components/accessibility/DyslexicModeToggle';
import EasyModeToggle from '@/components/accessibility/EasyModeToggle';
import Container from '@/components/layout/Container';

export default function Accessibility() {
  return (
    <Container as="section" className="accessibility-page">
      <header className="accessibility-page-header">
        <h1>Accessibility preferences</h1>
        <p>
          Tune the interface to match how you read best. These settings only apply on this device,
          and you can switch them off at any time.
        </p>
      </header>

      <div className="accessibility-card">
        <h2>Easy mode</h2>
        <p>
          Strip away visual noise and focus on primary actions. Easy Mode emphasises key flows, enlarges controls,
          and gently hides advanced options to reduce overwhelm.
        </p>
        <EasyModeToggle className="accessibility-toggle" />
        <ul>
          <li>Increases font sizes, button targets, and spacing for calmer scanning.</li>
          <li>Collapses secondary panels and dense UI controls until you need them.</li>
          <li>Remembers your choice on this browser so the site stays simplified.</li>
        </ul>
      </div>

      <div className="accessibility-card">
        <h2>Dyslexia-friendly mode</h2>
        <p>
          Swap to fonts, spacing, and emphasis designed to improve word recognition and lower visual stress.
        </p>
        <DyslexicModeToggle className="accessibility-toggle" />
        <ul>
          <li>Uses Atkinson Hyperlegible and Lexend fonts for clearer letterforms.</li>
          <li>Increases line, letter, and word spacing to prevent crowding.</li>
          <li>Activates stronger text decoration on links for easier scanning.</li>
        </ul>
      </div>

      <div className="accessibility-help">
        <h2>Need more options?</h2>
        <p>
          We&rsquo;re expanding our accessibility toolkit. Share feedback at{' '}
          <a href="mailto:accessibility@supportatlas.org">accessibility@supportatlas.org</a>.
        </p>
      </div>
    </Container>
  );
}
