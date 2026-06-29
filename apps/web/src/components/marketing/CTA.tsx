import React from 'react';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';

interface CTAProps {
  title?: string;
  description?: string;
  primaryLabel?: string;
  primaryHref?: string;
  secondaryLabel?: string;
  secondaryHref?: string;
}

export function CTA({
  title = 'Ready to find your perfect brand name?',
  description = 'Join 12,000+ founders who use Nomen to discover brands that are creative, available, and legally clear.',
  primaryLabel = 'Start for free',
  primaryHref = '/auth/register',
  secondaryLabel = 'See pricing',
  secondaryHref = '/pricing',
}: CTAProps) {
  return (
    <section
      className="relative overflow-hidden bg-indigo-600 py-20 lg:py-28"
      aria-labelledby="cta-heading"
    >
      {/* Background pattern */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 opacity-10"
        style={{
          backgroundImage:
            'radial-gradient(circle at 20% 50%, white 1px, transparent 1px), radial-gradient(circle at 80% 50%, white 1px, transparent 1px)',
          backgroundSize: '60px 60px',
        }}
      />

      <div className="relative mx-auto max-w-4xl px-6 text-center">
        <h2
          id="cta-heading"
          className="text-4xl font-extrabold tracking-tight text-white sm:text-5xl"
        >
          {title}
        </h2>
        <p className="mx-auto mt-5 max-w-xl text-lg text-indigo-100">{description}</p>

        <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
          <Link
            href={primaryHref}
            id="cta-primary-btn"
            className="inline-flex h-12 items-center gap-2 rounded-xl bg-white px-8 text-base font-semibold text-indigo-600 shadow-lg transition-all hover:bg-indigo-50 hover:shadow-xl hover:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-indigo-600"
          >
            {primaryLabel}
            <ArrowRight size={16} />
          </Link>
          {secondaryLabel && (
            <Link
              href={secondaryHref || '/pricing'}
              className="inline-flex h-12 items-center rounded-xl border border-indigo-400 px-8 text-base font-semibold text-white transition-all hover:border-white hover:bg-indigo-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white"
            >
              {secondaryLabel}
            </Link>
          )}
        </div>
      </div>
    </section>
  );
}
