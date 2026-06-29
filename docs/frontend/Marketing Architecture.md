# Marketing Website Architecture

## Directory Structure

The marketing experience is isolated within the `(marketing)` route group using Next.js App Router. This keeps the marketing files completely separate from the dashboard and authentication routes:

```text
apps/web/src/app/(marketing)/
├── page.tsx                     # Landing Page
├── pricing/page.tsx             # Pricing (with monthly/annual toggles)
├── features/page.tsx            # Features detailed overview
├── about/page.tsx               # Mission and core values
├── contact/page.tsx             # Zod validated contact form
├── faq/page.tsx                 # Accordion-style help center
├── blog/page.tsx                # Publications grid
├── blog/[slug]/page.tsx         # Dynamic dynamic-slug reader
├── docs/page.tsx                # Technical documentation index
├── careers/page.tsx             # Jobs directory
├── privacy/page.tsx             # Privacy Policy (Legal)
├── terms/page.tsx               # Terms of Service (Legal)
├── cookies/page.tsx             # Cookie policy (Legal)
├── dmca/page.tsx                # DMCA compliance notice (Legal)
├── changelog/page.tsx           # Platform release timeline (v0.1.0 - v0.5.0)
├── status/page.tsx              # System component health monitor
└── layout.tsx                   # Layout containing sticky Navbar + Footer
```

## Shared UI Components

We created reusable marketing components inside `components/marketing/` that are modular and structured:

- `Section.tsx`: Common padding/margin scales.
- `Navbar.tsx`: Sticky navigation with glassmorphism backdrop filter and responsive slide-out menus.
- `Footer.tsx`: Information links and live system health badge indicator.
- `Hero.tsx`: Title animations and interactive dashboard previews.
- `Stats.tsx`: Key metrics blocks.
- `FeatureCard.tsx`: Hover-lift effects with multiple custom brand accents.
- `PricingCard.tsx`: Plans presentation cards supporting billing cycle switches.
- `Testimonials.tsx`: Customer quote blocks in a balanced masonry grid.
- `FAQ.tsx`: Keyboard accessible collapsible rows.
- `CTA.tsx`: Visual conversion anchors.
- `Newsletter.tsx`: Newsletter subscribe forms backed by provider integrations.
- `BlogCard.tsx`: Media-styled list elements.
- `LogoCloud.tsx`: Trust signals container.

## Markdown Blog Engine

The blog uses file-based content routing loading `.md` files directly from `apps/web/content/blog/` using `fs` and `path`.
- YAML Frontmatter parsed using a custom non-regex utility method in `lib/blog.ts`.
- Content parsed and formatted dynamically into styled HTML tags during render.
- Automatically calculates estimated reading times (at 200 words-per-minute scale).
- Resolves related posts matching similar tag intersections.
- Statically generated via `generateStaticParams` for high speed.
