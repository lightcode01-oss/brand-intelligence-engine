import type { Metadata } from 'next';
import React from 'react';
import { Section, SectionHeading } from '@/components/marketing/Section';
import { FAQ } from '@/components/marketing/FAQ';
import { CTA } from '@/components/marketing/CTA';
import { generateSEO, faqSchema } from '@/lib/seo';

const FAQ_LIST = [
  {
    question: 'What is Nomen and how does it help founders?',
    answer:
      'Nomen is an AI-powered brand intelligence platform. It helps founders generate creative name ideas and instantly validates them against real-time domain registries, social handle APIs, and trademark filing databases so you only select names that are available.',
  },
  {
    question: 'How do you check for trademarks?',
    answer:
      'We run automated clearance searches against official databases like the USPTO and international trademark records. We calculate phonetics, spelling similarities, and category overlap to score name candidates from low to high risk. This serves as a preliminary filter before consulting formal legal counsel.',
  },
  {
    question: 'What domain TLDs does Nomen search?',
    answer:
      'We search over 50 popular extensions including .com, .io, .ai, .co, .net, .org, and newer developer-focused registries like .dev and .app.',
  },
  {
    question: 'Are there monthly generation limits on the Free plan?',
    answer:
      'Yes, the Free plan starts with 10 AI brand generations and 5 CSV/PDF report exports per month. You can upgrade to our paid tiers (Starter, Pro, Business) to access up to 2,000+ generations, full trademark scans, bulk inputs, and custom API access.',
  },
  {
    question: 'Can I cancel my subscription anytime?',
    answer:
      'Yes, absolutely. You can cancel or modify your active subscription plan at any time through our self-service billing customer portal. Changes take effect at the end of your current billing period, and we support instant resumes before the cycle resets.',
  },
  {
    question: 'How do I generate API keys to use Nomen programmatically?',
    answer:
      'If you have a Pro or Business account, you can create API keys in your Developer settings. These keys can be configured with specific scopes (such as checking domain availability or triggering generator tasks) and rotated periodically.',
  },
];

export const metadata: Metadata = generateSEO({
  title: 'FAQ',
  description: 'Find answers to common questions about Nomen\'s naming generator, domain searches, trademark risk scoring, and plans.',
  keywords: ['nomen faq', 'brand tool questions', 'faq brand score', 'trademark faq'],
  path: '/faq',
});

export default function FAQPage() {
  const jsonLd = faqSchema(FAQ_LIST);

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <Section className="pt-32" narrow>
        <SectionHeading
          eyebrow="Help Center"
          title="Frequently Asked Questions"
          description="Find quick answers to common queries regarding brand generation, domain registries, billing, and team features."
        />
        <div className="mt-12 rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
          <FAQ items={FAQ_LIST} />
        </div>
      </Section>
      <CTA />
    </>
  );
}
