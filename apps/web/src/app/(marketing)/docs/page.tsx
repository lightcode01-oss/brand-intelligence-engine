import type { Metadata } from 'next';
import React from 'react';
import { Section, SectionHeading } from '@/components/marketing/Section';
import { generateSEO } from '@/lib/seo';
import { BookOpen, Key, Globe, CreditCard, BrainCircuit, FileDown, HelpCircle, ArrowRight } from 'lucide-react';
import Link from 'next/link';

export const metadata: Metadata = generateSEO({
  title: 'Documentation',
  description:
    'Read guides and API specifications to integrate and optimize brand intelligence using Nomen.',
  keywords: ['nomen api documentation', 'developer guides', 'brand score guidelines', 'auth documentation'],
  path: '/docs',
});

const DOC_SECTIONS = [
  {
    icon: BookOpen,
    title: 'Getting Started',
    description: 'Learn the core concepts of brand intelligence, linguistic scoring, and starting your first project.',
    links: ['Platform Overview', 'Quickstart Guide', 'Workspace Architecture'],
  },
  {
    icon: Key,
    title: 'Authentication',
    description: 'Secure your requests with OAuth or custom JSON Web Tokens (JWT). Handle permissions and rotations.',
    links: ['JWT Token Flow', 'API Key Rotation', 'Scope Permissions'],
  },
  {
    icon: Globe,
    title: 'API Reference',
    description: 'Integrate live domain check, trademark scans, and generation engines directly into your applications.',
    links: ['Endpoints Spec', 'Rate Limits', 'Webhook Signatures'],
  },
  {
    icon: CreditCard,
    title: 'Billing & Subscriptions',
    description: 'Understand subscription lifecycle states, credits transactions, invoices, and self-service portals.',
    links: ['Stripe Setup', 'Usage Reset Schedule', 'Credit Balance API'],
  },
  {
    icon: BrainCircuit,
    title: 'AI Naming Engine',
    description: 'Fine-tune generator models, linguistics thresholds, syllables, and local Ollama server configurations.',
    links: ['Linguistic Algorithms', 'Provider Options', 'Category Phonetic Tuning'],
  },
  {
    icon: FileDown,
    title: 'Exports & Reports',
    description: 'Generate reports programmatically. Export details to PDF or tabular CSV files seamlessly.',
    links: ['PDF Layout Customization', 'Batch CSV Imports', 'Reports Delivery webhook'],
  },
  {
    icon: HelpCircle,
    title: 'Support & FAQ',
    description: 'Troubleshoot error codes, payload parameters, rate limit failures, or contact dedicated sales engineers.',
    links: ['Common Error Codes', 'API Limits FAQ', 'Contact support'],
  },
];

export default function DocsPage() {
  return (
    <Section className="pt-32">
      <SectionHeading
        eyebrow="Developer Center"
        title="Nomen Platform Documentation"
        description="Comprehensive guides, API specifications, and SDK integration rules for Nomen developers."
      />

      <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3 mt-12">
        {DOC_SECTIONS.map((section, idx) => (
          <div
            key={idx}
            className="flex flex-col rounded-2xl border border-slate-200 bg-white p-6 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
              <section.icon size={20} />
            </div>
            <h2 className="text-lg font-bold text-slate-900 mb-2">{section.title}</h2>
            <p className="text-sm text-slate-500 leading-relaxed mb-6 flex-1">
              {section.description}
            </p>
            <ul className="space-y-2 border-t border-slate-100 pt-4" role="list">
              {section.links.map((link, lIdx) => (
                <li key={lIdx}>
                  <Link
                    href="#"
                    className="inline-flex items-center gap-1 text-sm font-semibold text-indigo-600 hover:text-indigo-700"
                  >
                    <ArrowRight size={12} />
                    {link}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </Section>
  );
}
