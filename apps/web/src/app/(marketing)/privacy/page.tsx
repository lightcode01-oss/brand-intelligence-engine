import type { Metadata } from 'next';
import React from 'react';
import { Section, SectionHeading } from '@/components/marketing/Section';
import { generateSEO } from '@/lib/seo';

export const metadata: Metadata = generateSEO({
  title: 'Privacy Policy',
  description: 'Understand how Nomen collects, processes, and protects your corporate data and usage logs.',
  keywords: ['privacy policy', 'nomen gdpr compliance', 'user log security'],
  path: '/privacy',
});

export default function PrivacyPage() {
  return (
    <Section className="pt-32" narrow>
      <SectionHeading title="Privacy Policy" eyebrow="Legal" />
      <div className="prose text-slate-700 leading-relaxed space-y-6 pt-4">
        <p className="text-sm text-slate-400">Last updated: June 29, 2026</p>
        <p>
          At Nomen, we are committed to protecting your privacy. This Privacy Policy describes
          how we collect, use, and share your personal information when you use our Brand
          Intelligence Platform.
        </p>

        <h2 className="text-xl font-bold text-slate-900 pt-4">1. Information We Collect</h2>
        <p>
          We collect personal details like your name, email address, password, company name,
          and credit card details when you create an account, upgrade your plan, or contact us.
          We also log generator prompts, search queries, and analytics events during usage.
        </p>

        <h2 className="text-xl font-bold text-slate-900 pt-4">2. How We Use Your Information</h2>
        <p>
          We use the collected information to provision workspaces, resolve domain availability,
          verify trademark databases, run brand score metrics, generate secure API keys, and track
          metered credit limits. We do not sell your brand prompts to third parties.
        </p>

        <h2 className="text-xl font-bold text-slate-900 pt-4">3. Data Retention and Deletion</h2>
        <p>
          We retain your information as long as your subscription is active. You can request deletion
          of your workspace, historical generations, and personal profile at any time by contacting
          our support desk.
        </p>

        <h2 className="text-xl font-bold text-slate-900 pt-4">4. Cookies and Tracking</h2>
        <p>
          We use analytical cookies to verify login status, remember theme preferences, and track
          system errors. You can disable cookies in your browser settings, though some features may fail to load.
        </p>
      </div>
    </Section>
  );
}
