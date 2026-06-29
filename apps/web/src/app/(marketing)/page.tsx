import type { Metadata } from 'next';
import { Hero } from '@/components/marketing/Hero';
import { Stats } from '@/components/marketing/Stats';
import { LogoCloud } from '@/components/marketing/LogoCloud';
import { Section, SectionHeading } from '@/components/marketing/Section';
import { FeatureCard } from '@/components/marketing/FeatureCard';
import { Testimonials } from '@/components/marketing/Testimonials';
import { PricingCard, PricingTier } from '@/components/marketing/PricingCard';
import { FAQ } from '@/components/marketing/FAQ';
import { CTA } from '@/components/marketing/CTA';
import { Newsletter } from '@/components/marketing/Newsletter';
import {
  Globe, Shield, BarChart3, Users, Download, Sparkles
} from 'lucide-react';
import { generateSEO, organizationSchema, softwareApplicationSchema } from '@/lib/seo';

export const metadata: Metadata = generateSEO({
  title: 'Nomen — AI Brand Intelligence Platform',
  description:
    'Generate AI-powered brand names, validate domains, check trademarks, and score your brand — all in one intelligent pipeline. Start free.',
  keywords: ['brand naming', 'AI brand name generator', 'trademark search', 'domain availability', 'brand intelligence'],
  path: '/',
});

const FEATURES = [
  {
    icon: Sparkles,
    title: 'AI Name Generation',
    description: 'Generate hundreds of creative, on-brand name candidates using state-of-the-art LLMs tuned for brand linguistics.',
    accent: 'indigo' as const,
  },
  {
    icon: Globe,
    title: 'Domain Validation',
    description: 'Check availability across 50+ TLDs instantly. Never fall in love with a name before knowing its domain status.',
    accent: 'cyan' as const,
  },
  {
    icon: Shield,
    title: 'Trademark Analysis',
    description: 'Real-time USPTO and international trademark database queries with AI-powered conflict scoring.',
    accent: 'violet' as const,
  },
  {
    icon: BarChart3,
    title: 'Brand Score',
    description: 'Every name receives a composite score covering memorability, pronunciation, distinctiveness, and legal risk.',
    accent: 'emerald' as const,
  },
  {
    icon: Users,
    title: 'Team Collaboration',
    description: 'Invite your team, vote on candidates, leave feedback, and align on your brand without the meeting overhead.',
    accent: 'amber' as const,
  },
  {
    icon: Download,
    title: 'Export Engine',
    description: 'Export brand reports as PDFs, CSVs, or share directly with stakeholders via secure links.',
    accent: 'rose' as const,
  },
];

const PRICING_TIERS: PricingTier[] = [
  {
    name: 'Free',
    monthlyPrice: 0,
    yearlyPrice: 0,
    description: 'Perfect for exploring your first brand idea.',
    features: ['10 generations/month', '5 exports/month', '1 workspace', 'Domain validation', 'Basic brand score'],
    cta: 'Start for free',
    ctaHref: '/auth/register',
  },
  {
    name: 'Pro',
    monthlyPrice: 29,
    yearlyPrice: 24,
    description: 'For serious founders and growing teams.',
    features: ['500 generations/month', '200 exports/month', '5 workspaces', 'Trademark analysis', 'Advanced brand score', 'Priority support', 'Logo recommendations'],
    cta: 'Start Pro trial',
    ctaHref: '/auth/register?plan=pro',
    highlighted: true,
    badge: 'Most Popular',
  },
  {
    name: 'Business',
    monthlyPrice: 99,
    yearlyPrice: 82,
    description: 'For agencies and brand-heavy organizations.',
    features: ['2,000 generations/month', '1,000 exports/month', '20 workspaces', 'All AI providers', 'Bulk generation', 'API access', 'Team management', 'Custom integrations'],
    cta: 'Start Business trial',
    ctaHref: '/auth/register?plan=business',
  },
];

const FAQ_ITEMS = [
  {
    question: 'How does the AI name generation work?',
    answer: 'Nomen uses large language models trained on brand naming principles, linguistics, and market patterns. You provide a brief describing your product and target market, and our pipeline generates hundreds of candidates ranked by brand strength.',
  },
  {
    question: 'Is the trademark analysis legally binding?',
    answer: 'No. Nomen provides trademark risk scoring as a decision-support tool, not legal advice. You should always consult a qualified trademark attorney before filing or committing to a brand name.',
  },
  {
    question: 'How accurate is the domain availability check?',
    answer: 'We check domain availability in real time using RDAP and WHOIS protocols across 50+ TLDs. Results are accurate at the time of query; domains can be registered between when you check and when you purchase.',
  },
  {
    question: 'Can I export my brand reports?',
    answer: 'Yes. All plans include PDF and CSV export. Pro and above can export full brand intelligence reports including trademark risk summaries, domain availability tables, and brand score breakdowns.',
  },
  {
    question: 'What AI models does Nomen use?',
    answer: 'Nomen integrates with Google Gemini, OpenAI GPT-4, Anthropic Claude, and local Ollama models. The active provider is configurable per workspace. Pro plans get access to all providers.',
  },
];

export default function LandingPage() {
  const jsonLd = [organizationSchema(), softwareApplicationSchema()];

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      {/* Hero */}
      <Hero />

      {/* Stats */}
      <Stats />

      {/* Logo cloud */}
      <LogoCloud />

      {/* Features */}
      <Section id="features">
        <SectionHeading
          eyebrow="Platform Features"
          title="Everything your brand needs, in one place"
          description="Nomen combines AI generation with real-world validation to give you brand names that are creative and actually buildable."
        />
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((feature) => (
            <FeatureCard key={feature.title} {...feature} />
          ))}
        </div>
      </Section>

      {/* AI Workflow diagram */}
      <section className="bg-slate-50 py-20" id="how-it-works" aria-labelledby="workflow-heading">
        <div className="mx-auto max-w-7xl px-6">
          <SectionHeading
            eyebrow="How It Works"
            title="From brief to brand in minutes"
            description="Our 8-stage intelligence pipeline processes every name through linguistic, legal, and digital filters."
          />
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4" role="list" aria-label="Pipeline stages">
            {['Input Brief', 'AI Generation', 'Domain Check', 'Trademark Scan', 'Social Handles', 'Brand Scoring', 'Ranking', 'Export'].map(
              (stage, i) => (
                <div
                  key={stage}
                  role="listitem"
                  className="flex flex-col items-center gap-2 rounded-xl border border-slate-200 bg-white p-4 text-center shadow-sm"
                >
                  <span className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-100 text-sm font-bold text-indigo-700">
                    {i + 1}
                  </span>
                  <span className="text-xs font-medium text-slate-700">{stage}</span>
                </div>
              )
            )}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <Testimonials />

      {/* Pricing */}
      <Section id="pricing">
        <SectionHeading
          eyebrow="Simple Pricing"
          title="Start free, scale as you grow"
          description="No hidden fees. Cancel anytime. All plans include a 14-day Pro trial."
        />
        <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
          {PRICING_TIERS.map((tier) => (
            <PricingCard key={tier.name} tier={tier} yearly={false} />
          ))}
        </div>
      </Section>

      {/* FAQ */}
      <Section narrow className="bg-slate-50" id="faq">
        <SectionHeading
          eyebrow="FAQ"
          title="Common questions"
        />
        <FAQ items={FAQ_ITEMS} />
      </Section>

      {/* Newsletter */}
      <Newsletter />

      {/* Final CTA */}
      <CTA />
    </>
  );
}
