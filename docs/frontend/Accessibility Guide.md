# Accessibility and Usability Standards (WCAG AA Compliance)

## Coding Standards

Nomen is built to meet WCAG AA standards. We avoid visual-only styling by backing layout states with clean markup:

- **Semantic HTML**: We use `<header>`, `<main>`, `<footer>`, `<article>`, `<time>`, and `<section>` tags appropriately.
- **ARIA Roles**: Explicit roles are attached to custom components (e.g. `role="list"`, `role="listitem"`, `role="region"`, `role="contentinfo"`).
- **Form Controls**: All inputs are coupled to specific `htmlFor` label tags, and use screen-reader-only labels (`sr-only`) where visual titles are hidden.

## Keyboard Nav & State Visuals

The marketing website supports full keyboard navigation:
- **Interactive Triggers**: Collapsible accordion items use standard `<button>` tags mapping `aria-expanded` and `aria-controls` to the toggle container.
- **Focus Indicators**: Focus indicators are styled cleanly (e.g. `focus-visible:ring-2 focus-visible:ring-indigo-600 focus-visible:ring-offset-2`).
- **WAI-ARIA Accordions**: Accordions toggle their visibility states properly, mapping changes to screen readers instantly.
