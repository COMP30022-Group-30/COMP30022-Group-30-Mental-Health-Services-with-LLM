import DyslexicModeToggle from '@/components/accessibility/DyslexicModeToggle';
import EasyModeToggle from '@/components/accessibility/EasyModeToggle';
import HighContrastModeToggle from '@/components/accessibility/HighContrastModeToggle';
import ScreenReaderModeToggle from '@/components/accessibility/ScreenReaderModeToggle';
import LargeTextModeToggle from '@/components/accessibility/LargeTextModeToggle';
import ReducedMotionModeToggle from '@/components/accessibility/ReducedMotionModeToggle';
import Container from '@/components/layout/Container';

export default function Accessibility() {
  return (
    <Container as="section" className="accessibility-page">
      <header className="accessibility-page-header">
        <h1>Accessibility preferences</h1>
        <p>
          Pick the support you need and we&rsquo;ll remember it on this device. Start with the mode that sounds closest to
          what you need—you can switch on more than one and turn them off anytime.
        </p>
      </header>

      <nav className="accessibility-quick-links" aria-label="Accessibility categories">
        <a href="#reduce-overwhelm">Reduce overwhelm</a>
        <a href="#improve-readability">Improve readability</a>
        <a href="#boost-clarity">Boost clarity &amp; assistive tech</a>
      </nav>

      <section id="reduce-overwhelm" className="accessibility-section">
        <header className="accessibility-section-header">
          <h2>Reduce overwhelm</h2>
          <p>These options calm the layout and limit motion when the interface feels busy or distracting.</p>
        </header>
        <div className="accessibility-grid">
          <article className="accessibility-card" aria-labelledby="easy-mode-heading">
            <header>
              <h3 id="easy-mode-heading">Easy mode</h3>
              <p>Streamlines navigation, enlarges buttons, and hides advanced controls until you need them.</p>
            </header>
            <EasyModeToggle className="accessibility-toggle" />
            <ul>
              <li>Highlights one primary action per page.</li>
              <li>Makes buttons, lists, and spacing larger for calmer scanning.</li>
              <li>Remembers your choice for future visits on this browser.</li>
            </ul>
          </article>

          <article className="accessibility-card" aria-labelledby="reduced-motion-heading">
            <header>
              <h3 id="reduced-motion-heading">Reduced motion</h3>
              <p>Removes motion that can cause fatigue or dizziness while keeping the site fully functional.</p>
            </header>
            <ReducedMotionModeToggle className="accessibility-toggle" />
            <ul>
              <li>Disables decorative animations and parallax effects.</li>
              <li>Stops auto-scrolling transitions so content stays still.</li>
              <li>Slows down any essential feedback that still appears.</li>
            </ul>
          </article>
        </div>
      </section>

      <section id="improve-readability" className="accessibility-section">
        <header className="accessibility-section-header">
          <h2>Improve readability</h2>
          <p>Tune typography so words are easier to recognise and follow from line to line.</p>
        </header>
        <div className="accessibility-grid">
          <article className="accessibility-card" aria-labelledby="large-text-heading">
            <header>
              <h3 id="large-text-heading">Large text mode</h3>
              <p>Scales up all typography, spacing, and touch targets for low-vision or fatigue-friendly reading.</p>
            </header>
            <LargeTextModeToggle className="accessibility-toggle" />
            <ul>
              <li>Raises base text size across the app to about 125%.</li>
              <li>Widens line spacing and paragraph spacing for smoother tracking.</li>
              <li>Expands form inputs and buttons for easier tapping or clicking.</li>
            </ul>
          </article>

          <article className="accessibility-card" aria-labelledby="dyslexic-mode-heading">
            <header>
              <h3 id="dyslexic-mode-heading">Dyslexia-friendly mode</h3>
              <p>Switches to dyslexia-aware fonts and spacing to reduce visual crowding and letter flipping.</p>
            </header>
            <DyslexicModeToggle className="accessibility-toggle" />
            <ul>
              <li>Uses Atkinson Hyperlegible and Lexend typefaces with clearer letterforms.</li>
              <li>Boosts spacing between lines, letters, and words.</li>
              <li>Emphasises links with thicker underlines and contrast.</li>
            </ul>
          </article>
        </div>
      </section>

      <section id="boost-clarity" className="accessibility-section">
        <header className="accessibility-section-header">
          <h2>Boost clarity &amp; assistive tech</h2>
          <p>Enhance contrast and expose extra structure to help screen readers and keyboard users orient quickly.</p>
        </header>
        <div className="accessibility-grid">
          <article className="accessibility-card" aria-labelledby="high-contrast-heading">
            <header>
              <h3 id="high-contrast-heading">High contrast + color blind safe palette</h3>
              <p>Applies a bold palette designed for both high contrast and common color-vision conditions.</p>
            </header>
            <HighContrastModeToggle className="accessibility-toggle" />
            <ul>
              <li>Introduces dark surfaces with bright, non-conflicting highlights.</li>
              <li>Strengthens outlines, focus states, and link styles.</li>
              <li>Keeps alert colors distinguishable without relying on red/green contrast.</li>
            </ul>
          </article>

          <article className="accessibility-card" aria-labelledby="screen-reader-heading">
            <header>
              <h3 id="screen-reader-heading">Screen reader assist</h3>
              <p>Surfaces skip links and extra context for landmark regions to speed up navigation with assistive tech.</p>
            </header>
            <ScreenReaderModeToggle className="accessibility-toggle" />
            <ul>
              <li>Makes skip links and region labels visible at the top of each page.</li>
              <li>Strengthens focus outlines for keyboard navigation.</li>
              <li>Adds helper text to explain layout changes and live regions.</li>
            </ul>
          </article>
        </div>
      </section>
    </Container>
  );
}
