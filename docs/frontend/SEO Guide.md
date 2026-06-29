# SEO Best Practices and Configuration Guide

## Configuration Framework

Nomen implements automated SEO metadata inside `src/lib/seo.ts` using Next.js `Metadata` primitives.

```typescript
export function generateSEO({
  title,
  description,
  keywords,
  path,
  image,
  noIndex,
  type,
  publishedAt,
  author
}: SEOProps): Metadata;
```

Every public route includes:
- **Title and Description**: Describing core functionality.
- **Canonical URLs**: Generated dynamically based on `NEXT_PUBLIC_APP_URL`.
- **OpenGraph & Twitter Cards**: High-res preview cards formatted for platforms.
- **Robots Directives**: Structured controls permitting indexing across search pages.

## Crawling Infrastructure

We configure Search Engine Crawling directly from App Router root files:

1. **`robots.ts`**: Maps User-Agent access, permitting crawling on indexable items while blocking authentication subtrees, dashboard components, and webhooks endpoints.
2. **`sitemap.ts`**: Resolves all marketing URLs alongside dynamically loaded blog post slugs.
3. **`manifest.ts`**: Configures app standalone parameters, branding colors (`#4f46e5`), and asset sizes for responsive launcher screens.

## Structured Data (JSON-LD)

To stand out in search results, Nomen implements key Schema.org structures:
- **Organization Schema**: Identifies corporate contacts and repository sites.
- **SoftwareApplication Schema**: Catalogues SaaS features, prices, and software category tags.
- **FAQ Schema**: Standardizes Q&A pairs for inline answers on search result pages.
- **Breadcrumbs Schema**: Standardizes user hierarchy trails inside dynamic blog article routes.
