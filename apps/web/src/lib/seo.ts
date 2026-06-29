import type { Metadata } from 'next';

const BASE_URL = process.env.NEXT_PUBLIC_APP_URL || 'https://nomen.ai';
const SITE_NAME = 'Nomen';
const TWITTER_HANDLE = '@nomenai';

interface SEOProps {
  title: string;
  description: string;
  keywords?: string[];
  path?: string;
  image?: string;
  noIndex?: boolean;
  type?: 'website' | 'article';
  publishedAt?: string;
  author?: string;
}

/**
 * Generates fully-typed Next.js Metadata for any page.
 * Includes OpenGraph, Twitter Cards, canonical URL, and robots directives.
 */
export function generateSEO({
  title,
  description,
  keywords = [],
  path = '',
  image = '/og-default.png',
  noIndex = false,
  type = 'website',
  publishedAt,
  author,
}: SEOProps): Metadata {
  const url = `${BASE_URL}${path}`;
  const ogImage = image.startsWith('http') ? image : `${BASE_URL}${image}`;
  const fullTitle = title === SITE_NAME ? title : `${title} — ${SITE_NAME}`;

  return {
    title: fullTitle,
    description,
    keywords: keywords.join(', '),
    metadataBase: new URL(BASE_URL),
    alternates: {
      canonical: url,
    },
    robots: {
      index: !noIndex,
      follow: !noIndex,
      googleBot: {
        index: !noIndex,
        follow: !noIndex,
        'max-video-preview': -1,
        'max-image-preview': 'large',
        'max-snippet': -1,
      },
    },
    openGraph: {
      title: fullTitle,
      description,
      url,
      siteName: SITE_NAME,
      locale: 'en_US',
      type,
      images: [
        {
          url: ogImage,
          width: 1200,
          height: 630,
          alt: fullTitle,
        },
      ],
      ...(publishedAt && { publishedTime: publishedAt }),
      ...(author && { authors: [author] }),
    },
    twitter: {
      card: 'summary_large_image',
      title: fullTitle,
      description,
      images: [ogImage],
      creator: TWITTER_HANDLE,
      site: TWITTER_HANDLE,
    },
  };
}

/** JSON-LD structured data for the organisation. */
export function organizationSchema() {
  return {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: SITE_NAME,
    url: BASE_URL,
    logo: `${BASE_URL}/logo.png`,
    description: 'AI-powered brand intelligence and name discovery platform.',
    sameAs: [
      'https://twitter.com/nomenai',
      'https://github.com/lightcode01-oss/brand-intelligence-engine',
    ],
    contactPoint: {
      '@type': 'ContactPoint',
      email: 'hello@nomen.ai',
      contactType: 'customer support',
    },
  };
}

/** JSON-LD structured data for the SaaS application. */
export function softwareApplicationSchema() {
  return {
    '@context': 'https://schema.org',
    '@type': 'SoftwareApplication',
    name: SITE_NAME,
    applicationCategory: 'BusinessApplication',
    operatingSystem: 'Web',
    url: BASE_URL,
    description:
      'AI-Powered Brand Name Generation, Domain Validation, Trademark Search, and Brand Intelligence Platform.',
    offers: [
      { '@type': 'Offer', price: '0', priceCurrency: 'USD', name: 'Free' },
      { '@type': 'Offer', price: '9', priceCurrency: 'USD', name: 'Starter' },
      { '@type': 'Offer', price: '29', priceCurrency: 'USD', name: 'Pro' },
      { '@type': 'Offer', price: '99', priceCurrency: 'USD', name: 'Business' },
    ],
  };
}

/** JSON-LD FAQ schema from a list of QA pairs. */
export function faqSchema(items: { question: string; answer: string }[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: items.map(({ question, answer }) => ({
      '@type': 'Question',
      name: question,
      acceptedAnswer: { '@type': 'Answer', text: answer },
    })),
  };
}

/** JSON-LD breadcrumb schema. */
export function breadcrumbSchema(crumbs: { name: string; url: string }[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: crumbs.map((crumb, idx) => ({
      '@type': 'ListItem',
      position: idx + 1,
      name: crumb.name,
      item: crumb.url.startsWith('http') ? crumb.url : `${BASE_URL}${crumb.url}`,
    })),
  };
}
