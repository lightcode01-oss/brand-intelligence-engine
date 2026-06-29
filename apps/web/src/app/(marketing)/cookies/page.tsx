import type { Metadata } from 'next';
import React from 'react';
import { Section, SectionHeading } from '@/components/marketing/Section';
import { generateSEO } from '@/lib/seo';

export const metadata: Metadata = generateSEO({
  title: 'Cookie Policy',
  description: 'Learn how Nomen utilizes tracking, storage cookies, and browser preference variables.',
  keywords: ['cookie settings', 'essential cookies', 'nomen analytics cookies'],
  path: '/cookies',
});

export default function CookiesPage() {
  return (
    <Section className="pt-32" narrow>
      <SectionHeading title="Cookie Policy" eyebrow="Legal" />
      <div className="prose text-slate-700 leading-relaxed space-y-6 pt-4">
        <p className="text-sm text-slate-400">Last updated: June 29, 2026</p>
        <p>
          This Cookie Policy explains how Nomen, Inc. uses cookies and similar tracking technologies to
          verify user sessions, authenticate API workspace contexts, and monitor client experiences.
        </p>

        <h2 className="text-xl font-bold text-slate-900 pt-4">1. What Are Cookies?</h2>
        <p>
          Cookies are small text files downloaded by your web browser when you visit websites. They allow
          the platform to recognize your account profile, retain layout state, and store temporary authentication keys.
        </p>

        <h2 className="text-xl font-bold text-slate-900 pt-4">2. Types of Cookies We Use</h2>
        <ul className="list-disc pl-6 space-y-2" role="list">
          <li>
            <strong>Essential Cookies:</strong> Critical for security, CSRF defense, and session persistence.
            Disabling these will make the dashboard unusable.
          </li>
          <li>
            <strong>Preferences Cookies:</strong> Retain choices like theme preferences (dark/light mode) or default
            workspace layouts.
          </li>
          <li>
            <strong>Performance & Analytics:</strong> Provided by environment-driven integrations (e.g., Plausible, PostHog).
            They gather pageview counts without exposing personally identifiable information.
          </li>
        </ul>

        <h2 className="text-xl font-bold text-slate-900 pt-4">3. Managing Cookie Settings</h2>
        <p>
          You can modify or refuse cookies at any time via your browser settings. Be advised that blocking essential
          cookies will prevent login and restrict platform functions.
        </p>
      </div>
    </Section>
  );
}
