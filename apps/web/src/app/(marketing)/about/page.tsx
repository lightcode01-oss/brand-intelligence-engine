import type { Metadata } from 'next';
import React from 'react';
import { Section, SectionHeading } from '@/components/marketing/Section';
import { CTA } from '@/components/marketing/CTA';
import { generateSEO } from '@/lib/seo';
import { Users, Eye, Target, Award } from 'lucide-react';

export const metadata: Metadata = generateSEO({
  title: 'About Us',
  description:
    'Learn about Nomen, our mission to simplify brand identity, and the values that drive our technology team.',
  keywords: ['nomen company', 'about brand intelligence', 'nomen founders', 'ai naming team'],
  path: '/about',
});

const VALUES = [
  {
    icon: Target,
    title: 'Clarity Over Noise',
    description: 'We believe naming shouldn\'t be an endless guessing game. We deliver data-backed clarity so you can launch confidently.',
  },
  {
    icon: Eye,
    title: 'Linguistic Rigor',
    description: 'Names carry power. We run extensive phonetic, trademark, and linguistic analytics to ensure your name carries the right power.',
  },
  {
    icon: Users,
    title: 'Collaborative Spirit',
    description: 'No brand is built in isolation. We build tools that make it easy for partners, stakeholders, and teams to build together.',
  },
  {
    icon: Award,
    title: 'Absolute Quality',
    description: 'We provide agency-grade naming models, dynamic pipeline architectures, and sub-second validation engines to our users.',
  },
];

export default function AboutPage() {
  return (
    <>
      <Section className="pt-32">
        <SectionHeading
          eyebrow="Our Mission"
          title="Empowering builders to name their future"
          description="Nomen was founded with a simple belief: finding a clean, legally safe, and beautiful brand name shouldn't cost $50,000 or take three months."
        />

        <div className="mx-auto max-w-3xl mt-12 text-slate-600 text-lg leading-relaxed space-y-6">
          <p>
            Every year, millions of developers, founders, and creators start new projects. Yet
            one of the biggest bottlenecks they encounter is finding a brand identity. The domain
            names are taken, social handles are occupied, and trademark filings present a legal
            minefield.
          </p>
          <p>
            Traditionally, clearing this hurdle meant either hiring expensive naming agencies or
            spending weeks in spreadsheets manually copy-pasting domain and trademark searches.
            Nomen was built to automate the tedious steps while elevating the creative process.
          </p>
          <p>
            By combining advanced natural language engines with real-time validation endpoints,
            Nomen filters out unusable names before they reach your workspace. You see only what is
            available, clear, and phonetically strong.
          </p>
        </div>
      </Section>

      <section className="bg-slate-50 py-20 lg:py-28" aria-label="Our Values">
        <div className="mx-auto max-w-7xl px-6">
          <SectionHeading
            title="The values that guide us"
            description="Our core principles steer our features, algorithms, and service design."
          />
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
            {VALUES.map((value, idx) => (
              <div key={idx} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
                  <value.icon size={20} />
                </div>
                <h3 className="text-base font-semibold text-slate-900 mb-2">{value.title}</h3>
                <p className="text-sm text-slate-500 leading-relaxed">{value.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <CTA />
    </>
  );
}
