import type { Metadata } from 'next';
import React from 'react';
import { Section, SectionHeading } from '@/components/marketing/Section';
import { generateSEO } from '@/lib/seo';
import { GitCommit, Star, Rocket, ShieldAlert } from 'lucide-react';

export const metadata: Metadata = generateSEO({
  title: 'Changelog',
  description: 'Track updates, improvements, and releases for the Nomen Brand Platform.',
  keywords: ['nomen releases', 'changelog', 'platform updates'],
  path: '/changelog',
});

const RELEASES = [
  {
    version: 'v0.5.0',
    date: 'June 29, 2026',
    title: 'Payments, Subscriptions & Customer Portal',
    icon: Rocket,
    changes: [
      'Implemented primary Stripe Provider with proration and dynamic price lookups.',
      'Added secondary Lemon Squeezy provider via REST/httpx client.',
      'Created self-service Customer Portal endpoints for invoices and method updates.',
      'Introduced UsageEnforcementMiddleware checking limits before handler triggers.',
      'Added WebhookEvent database table with unique idempotency keys to prevent double-charges.',
    ],
  },
  {
    version: 'v0.3.0',
    date: 'June 10, 2026',
    title: 'SaaS Platform & Billing Foundation',
    icon: Star,
    changes: [
      'Created billing schemas including Plan, Subscription, Invoice, and UsageRecord.',
      'Built developer API key engine with secure SHA-256 storage and rotation.',
      'Implemented local billing service layers for usage reset and credit transactions.',
      'Added unit testing suites for token scopes and credit locking mechanisms.',
    ],
  },
  {
    version: 'v0.2.0',
    date: 'May 20, 2026',
    title: 'Production Infrastructure & Reliability',
    icon: ShieldAlert,
    changes: [
      'Containerized all backend and frontend microservices using multi-stage Docker builds.',
      'Configured local and production-grade Docker Compose stacks with Redis/PostgreSQL.',
      'Added healthcheck checks, Prometheus telemetry, and rate limiters.',
      'Constructed CI/CD workflows for automated builds and testing.',
    ],
  },
  {
    version: 'v0.1.0',
    date: 'April 15, 2026',
    title: 'Initial Core AI Pipelines',
    icon: GitCommit,
    changes: [
      'Designed the modular 8-stage brand generation pipeline with Orchestrator stages.',
      'Integrated dynamic AI provider registries discovering OpenAI, Gemini, and Claude.',
      'Added initial domain registry check and USPTO search queries.',
      'Configured PostgreSQL DB schemas, Alembic migrations, and security handlers.',
    ],
  },
];

export default function ChangelogPage() {
  return (
    <Section className="pt-32">
      <SectionHeading
        eyebrow="Updates"
        title="What's New in Nomen"
        description="Follow our product releases, developer updates, and infrastructure enhancements."
      />

      <div className="relative mx-auto max-w-3xl mt-16 pl-6 sm:pl-8 before:absolute before:left-3 before:top-2 before:bottom-2 before:w-[2px] before:bg-slate-200">
        {RELEASES.map((release, idx) => (
          <div key={idx} className="relative mb-12 last:mb-0">
            {/* Timeline icon dot */}
            <span className="absolute -left-[30px] sm:-left-[38px] top-1 flex h-6 w-6 items-center justify-center rounded-full bg-white border-2 border-indigo-600 text-indigo-600 shadow-sm">
              <release.icon size={12} />
            </span>

            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3 mb-4">
                <div>
                  <span className="inline-flex rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-bold text-indigo-700">
                    {release.version}
                  </span>
                  <h2 className="text-lg font-extrabold text-slate-900 mt-1">{release.title}</h2>
                </div>
                <time className="text-xs text-slate-400 font-semibold">{release.date}</time>
              </div>

              <ul className="list-disc pl-5 space-y-2 text-sm text-slate-600" role="list">
                {release.changes.map((change, cIdx) => (
                  <li key={cIdx}>{change}</li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>
    </Section>
  );
}
