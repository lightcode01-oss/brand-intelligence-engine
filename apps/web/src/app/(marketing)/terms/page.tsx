import type { Metadata } from 'next';
import React from 'react';
import { Section, SectionHeading } from '@/components/marketing/Section';
import { generateSEO } from '@/lib/seo';

export const metadata: Metadata = generateSEO({
  title: 'Terms of Service',
  description: 'Review the legal agreement and usage parameters governing the Nomen Brand Platform.',
  keywords: ['terms of service', 'nomen contract', 'billing terms'],
  path: '/terms',
});

export default function TermsPage() {
  return (
    <Section className="pt-32" narrow>
      <SectionHeading title="Terms of Service" eyebrow="Legal" />
      <div className="prose text-slate-700 leading-relaxed space-y-6 pt-4">
        <p className="text-sm text-slate-400">Last updated: June 29, 2026</p>
        <p>
          Welcome to Nomen. By accessing our platform, website, and developer APIs, you agree to
          be bound by these Terms of Service. Please read them carefully.
        </p>

        <h2 className="text-xl font-bold text-slate-900 pt-4">1. Scope of Service</h2>
        <p>
          Nomen provides AI-based name generation, composite score metrics, domain checks, and preliminary
          trademark search tools. The suggestions, clearance scores, and database matches do not constitute
          formal legal advice. Always consult a licensed attorney.
        </p>

        <h2 className="text-xl font-bold text-slate-900 pt-4">2. Account Responsibility</h2>
        <p>
          You are responsible for protecting your account credentials, workspace secrets, and API keys.
          Any metered operations (generations, exports, queries) triggered under your token credentials
          will bill against your plan limit balance.
        </p>

        <h2 className="text-xl font-bold text-slate-900 pt-4">3. Prohibited Usage</h2>
        <p>
          You agree not to exploit Nomen to scrape registries, distribute spam, reverse-engineer phonetic
          algorithms, or bypass metered API rate limiters. Violation of this clause will lead to account
          revocation.
        </p>

        <h2 className="text-xl font-bold text-slate-900 pt-4">4. Limitation of Liability</h2>
        <p>
          Nomen is provided on an &quot;as-is&quot; and &quot;as-available&quot; basis. We make no warranty that domain checks or
          trademark scans are 100% comprehensive, nor that name options will be free from future third-party litigation.
        </p>
      </div>
    </Section>
  );
}
