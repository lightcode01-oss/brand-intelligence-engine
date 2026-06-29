'use client';

import React, { useState } from 'react';
import { Section, SectionHeading } from '@/components/marketing/Section';
import { PricingCard, PricingTier } from '@/components/marketing/PricingCard';
import { CTA } from '@/components/marketing/CTA';
import { FAQ } from '@/components/marketing/FAQ';
import { Check, X } from 'lucide-react';

const TIERS: PricingTier[] = [
  {
    name: 'Free',
    monthlyPrice: 0,
    yearlyPrice: 0,
    description: 'For individual founders exploring their first brand idea.',
    features: [
      '10 generations/month',
      '5 exports/month',
      '1 workspace',
      '3 projects',
      '1 team member',
      'Domain validation',
      'Basic brand score',
      'Email support',
    ],
    cta: 'Start for free',
    ctaHref: '/auth/register',
  },
  {
    name: 'Starter',
    monthlyPrice: 9,
    yearlyPrice: 7,
    description: 'For solo founders who need more power without the enterprise price.',
    features: [
      '100 generations/month',
      '50 exports/month',
      '2 workspaces',
      '10 projects',
      '3 team members',
      'Domain validation',
      'Brand score',
      'Bulk generation',
      'Email support',
    ],
    cta: 'Start Starter',
    ctaHref: '/auth/register?plan=starter',
  },
  {
    name: 'Pro',
    monthlyPrice: 29,
    yearlyPrice: 24,
    description: 'The complete toolkit for serious founders and small teams.',
    features: [
      '500 generations/month',
      '200 exports/month',
      '5 workspaces',
      '50 projects',
      '10 team members',
      'Trademark analysis',
      'Advanced brand score',
      'All AI providers',
      'Logo recommendations',
      'Priority support',
      'API access',
    ],
    cta: 'Start Pro trial',
    ctaHref: '/auth/register?plan=pro',
    highlighted: true,
    badge: 'Most Popular',
  },
  {
    name: 'Business',
    monthlyPrice: 99,
    yearlyPrice: 82,
    description: 'For agencies and organizations managing multiple brands.',
    features: [
      '2,000 generations/month',
      '1,000 exports/month',
      '20 workspaces',
      'Unlimited projects',
      '50 team members',
      'All AI providers',
      'Bulk generation',
      'Full API access',
      'Team management',
      'Priority support',
      'Custom integrations',
      'SSO (coming soon)',
    ],
    cta: 'Start Business trial',
    ctaHref: '/auth/register?plan=business',
  },
  {
    name: 'Enterprise',
    monthlyPrice: 0,
    yearlyPrice: 0,
    description: 'Custom pricing for large teams with advanced compliance needs.',
    features: [
      'Unlimited everything',
      'Custom AI models',
      'Dedicated infrastructure',
      'SSO / SAML',
      'Audit logs',
      'Custom SLAs',
      'Dedicated success manager',
      'Custom integrations',
      'On-premise deployment',
    ],
    cta: 'Contact sales',
    ctaHref: '/contact',
  },
];

const COMPARISON = [
  { feature: 'Generations per month', free: '10', starter: '100', pro: '500', business: '2,000', enterprise: 'Unlimited' },
  { feature: 'Domain validation', free: true, starter: true, pro: true, business: true, enterprise: true },
  { feature: 'Trademark analysis', free: false, starter: false, pro: true, business: true, enterprise: true },
  { feature: 'Brand score', free: 'Basic', starter: 'Basic', pro: 'Advanced', business: 'Advanced', enterprise: 'Custom' },
  { feature: 'Bulk generation', free: false, starter: true, pro: true, business: true, enterprise: true },
  { feature: 'API access', free: false, starter: false, pro: true, business: true, enterprise: true },
  { feature: 'Team members', free: '1', starter: '3', pro: '10', business: '50', enterprise: 'Unlimited' },
  { feature: 'Workspaces', free: '1', starter: '2', pro: '5', business: '20', enterprise: 'Unlimited' },
  { feature: 'SSO / SAML', free: false, starter: false, pro: false, business: false, enterprise: true },
  { feature: 'Audit logs', free: false, starter: false, pro: false, business: false, enterprise: true },
  { feature: 'Support', free: 'Email', starter: 'Email', pro: 'Priority', business: 'Priority', enterprise: 'Dedicated' },
];

const FAQ_ITEMS = [
  {
    question: 'Can I change plans anytime?',
    answer: 'Yes. You can upgrade or downgrade your plan at any time. Upgrades apply immediately with proration. Downgrades apply at the end of the current billing period.',
  },
  {
    question: 'Is there a free trial?',
    answer: 'Yes. All paid plans come with a 14-day free trial. No credit card required to start.',
  },
  {
    question: 'What happens when I hit my generation limit?',
    answer: 'Your generations are paused until the next billing cycle. You can upgrade your plan to immediately resume access.',
  },
  {
    question: 'Do you offer annual discounts?',
    answer: 'Yes. Annual plans are billed at a 20% discount compared to monthly pricing.',
  },
];

function CellValue({ value }: { value: string | boolean }) {
  if (value === true) return <Check size={16} className="text-emerald-500 mx-auto" aria-label="Included" />;
  if (value === false) return <X size={16} className="text-slate-300 mx-auto" aria-label="Not included" />;
  return <span className="text-sm text-slate-700">{value}</span>;
}

export default function PricingPage() {
  const [yearly, setYearly] = useState(false);

  return (
    <>
      <Section className="pt-32">
        <div className="mb-14 text-center">
          <p className="mb-3 text-sm font-semibold uppercase tracking-widest text-indigo-600">
            Pricing
          </p>
          <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl">
            Simple, transparent pricing
          </h1>
          <p className="mx-auto mt-5 max-w-xl text-lg text-slate-500">
            Start free. Upgrade when you need more. Cancel anytime.
          </p>

          {/* Billing toggle */}
          <div className="mt-8 inline-flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 p-1.5">
            <button
              onClick={() => setYearly(false)}
              className={`rounded-lg px-5 py-2 text-sm font-semibold transition-all ${!yearly ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
              aria-pressed={!yearly}
            >
              Monthly
            </button>
            <button
              onClick={() => setYearly(true)}
              className={`rounded-lg px-5 py-2 text-sm font-semibold transition-all ${yearly ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
              aria-pressed={yearly}
            >
              Annual
              <span className="ml-2 rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-bold text-emerald-700">
                −20%
              </span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-3 lg:grid-cols-5">
          {TIERS.map((tier) => (
            <PricingCard key={tier.name} tier={tier} yearly={yearly} />
          ))}
        </div>
      </Section>

      {/* Comparison table */}
      <Section className="bg-slate-50">
        <SectionHeading title="Compare all features" align="center" />
        <div className="overflow-x-auto">
          <table className="w-full min-w-[700px] border-collapse text-sm" aria-label="Feature comparison table">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="py-3 pr-4 text-left font-semibold text-slate-500">Feature</th>
                {['Free', 'Starter', 'Pro', 'Business', 'Enterprise'].map((name) => (
                  <th key={name} className="px-4 py-3 text-center font-semibold text-slate-900">
                    {name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {COMPARISON.map((row, idx) => (
                <tr
                  key={row.feature}
                  className={`border-b border-slate-100 ${idx % 2 === 0 ? 'bg-white' : 'bg-slate-50'}`}
                >
                  <td className="py-3.5 pr-4 text-slate-700 font-medium">{row.feature}</td>
                  <td className="px-4 py-3.5 text-center"><CellValue value={row.free} /></td>
                  <td className="px-4 py-3.5 text-center"><CellValue value={row.starter} /></td>
                  <td className="px-4 py-3.5 text-center bg-indigo-50/50"><CellValue value={row.pro} /></td>
                  <td className="px-4 py-3.5 text-center"><CellValue value={row.business} /></td>
                  <td className="px-4 py-3.5 text-center"><CellValue value={row.enterprise} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>

      <Section narrow className="bg-white">
        <SectionHeading eyebrow="FAQ" title="Pricing questions" />
        <FAQ items={FAQ_ITEMS} />
      </Section>

      <CTA title="Start your 14-day free trial" secondaryLabel="Talk to sales" secondaryHref="/contact" />
    </>
  );
}
