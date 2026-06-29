import type { Metadata } from 'next';
import React from 'react';
import { Section, SectionHeading } from '@/components/marketing/Section';
import { FeatureCard } from '@/components/marketing/FeatureCard';
import { CTA } from '@/components/marketing/CTA';
import { generateSEO } from '@/lib/seo';
import {
  Sparkles,
  BarChart3,
  Globe,
  Shield,
  Search,
  Fingerprint,
  Users,
  Download,
  Code2,
} from 'lucide-react';

export const metadata: Metadata = generateSEO({
  title: 'Platform Features',
  description:
    'Explore the powerful brand intelligence toolkit. Generate names, validate domains, check trademarks, search social usernames, score brands, and collaborate.',
  keywords: ['brand generator features', 'trademark check', 'domain check', 'api access', 'brand scoring'],
  path: '/features',
});

const ALL_FEATURES = [
  {
    icon: Sparkles,
    title: 'AI Name Generation',
    description:
      'Generate hundreds of brand names tailored to your company description, target market, and linguistic style using state-of-the-art AI engines.',
    accent: 'indigo' as const,
  },
  {
    icon: Fingerprint,
    title: 'Brand Score',
    description:
      'Evaluate brand names across composite factors including memorability, pronounceability, visual aesthetics, and category fit using our proprietary algorithm.',
    accent: 'violet' as const,
  },
  {
    icon: Globe,
    title: 'Domain Validation',
    description:
      'Instantly check domain name availability across .com, .io, .ai, .co, and 50+ other top-level domains to secure your online presence.',
    accent: 'cyan' as const,
  },
  {
    icon: Shield,
    title: 'Trademark Search',
    description:
      'Search official trademark databases in real-time to identify potential conflicts and lower legal exposure before launch.',
    accent: 'emerald' as const,
  },
  {
    icon: Search,
    title: 'Social Username Search',
    description:
      'Verify username availability across Twitter/X, GitHub, Instagram, LinkedIn, and major developer sites in a single query.',
    accent: 'amber' as const,
  },
  {
    icon: BarChart3,
    title: 'Brand Intelligence',
    description:
      'Get granular analytics on brand phonetic patterns, syllables, length, and sentiment trends in your business category.',
    accent: 'rose' as const,
  },
  {
    icon: Users,
    title: 'Team Collaboration',
    description:
      'Share name shortlists, vote on candidates, collect member feedback, and coordinate naming sprints in shared workspaces.',
    accent: 'indigo' as const,
  },
  {
    icon: Download,
    title: 'Export Engine',
    description:
      'Generate professional PDF brand intelligence reports, download CSVs of verified shortlists, or export slides for stakeholders.',
    accent: 'cyan' as const,
  },
  {
    icon: Code2,
    title: 'Developer API Access',
    description:
      'Integrate domain, trademark, and naming algorithms directly into your product flow with our robust, low-latency REST API.',
    accent: 'violet' as const,
  },
];

export default function FeaturesPage() {
  return (
    <>
      <Section className="pt-32">
        <SectionHeading
          eyebrow="Toolkit"
          title="Supercharge your brand discovery"
          description="Everything you need to create, validate, and launch a legally clear, highly memorable brand name."
        />
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {ALL_FEATURES.map((feature, idx) => (
            <FeatureCard
              key={idx}
              icon={feature.icon}
              title={feature.title}
              description={feature.description}
              accent={feature.accent}
            />
          ))}
        </div>
      </Section>

      {/* Feature Deep Dive / Visual Walkthrough */}
      <section className="bg-slate-50 py-20 lg:py-28" aria-label="Feature deep dive">
        <div className="mx-auto max-w-7xl px-6">
          <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-2">
            <div>
              <span className="text-sm font-semibold uppercase tracking-widest text-indigo-600">
                Linguistic Analysis
              </span>
              <h2 className="mt-3 text-3xl font-bold text-slate-900 sm:text-4xl">
                Linguistic and brand score analysis
              </h2>
              <p className="mt-5 text-lg text-slate-600 leading-relaxed">
                Nomen is not just a generator. It&apos;s an intelligence filter. Our algorithm scores
                every name based on phonetic complexity, readability, and memorability so you can
                choose a name that sticks.
              </p>
              <ul className="mt-8 space-y-4 text-sm text-slate-700" role="list">
                <li className="flex items-center gap-3">
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-indigo-100 text-indigo-700 font-bold">✓</span>
                  Category phonetic affinity matching
                </li>
                <li className="flex items-center gap-3">
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-indigo-100 text-indigo-700 font-bold">✓</span>
                  Multilingual barrier checking (ensuring positive meanings globally)
                </li>
                <li className="flex items-center gap-3">
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-indigo-100 text-indigo-700 font-bold">✓</span>
                  Automatic spelling risk factor assessment
                </li>
              </ul>
            </div>
            <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-xl">
              <h3 className="text-lg font-bold text-slate-900 mb-6">Brand Score Profile</h3>
              <div className="space-y-6">
                {[
                  { name: 'Pronounceability', score: 94, color: 'bg-indigo-600' },
                  { name: 'Memorability', score: 88, color: 'bg-violet-600' },
                  { name: 'Phonetic Distinctiveness', score: 91, color: 'bg-cyan-600' },
                  { name: 'Linguistic Safety', score: 98, color: 'bg-emerald-600' },
                ].map((item, idx) => (
                  <div key={idx} className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="font-semibold text-slate-700">{item.name}</span>
                      <span className="font-bold text-slate-900">{item.score}%</span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                      <div
                        className={`h-full rounded-full ${item.color}`}
                        style={{ width: `${item.score}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <CTA />
    </>
  );
}
