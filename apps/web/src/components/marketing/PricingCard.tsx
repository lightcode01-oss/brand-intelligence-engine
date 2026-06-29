import React from 'react';
import { Check, Zap } from 'lucide-react';
import Link from 'next/link';
import { cn } from '@/lib/utils/cn';

export interface PricingTier {
  name: string;
  monthlyPrice: number;
  yearlyPrice: number;
  description: string;
  features: string[];
  cta: string;
  ctaHref: string;
  highlighted?: boolean;
  badge?: string;
}

interface PricingCardProps {
  tier: PricingTier;
  yearly: boolean;
}

export function PricingCard({ tier, yearly }: PricingCardProps) {
  const price = yearly ? tier.yearlyPrice : tier.monthlyPrice;
  const isEnterprise = tier.monthlyPrice === 0 && tier.name !== 'Free';

  return (
    <div
      className={cn(
        'relative flex flex-col rounded-2xl p-8 transition-all',
        tier.highlighted
          ? 'border-2 border-indigo-600 bg-indigo-600 text-white shadow-2xl shadow-indigo-200'
          : 'border border-slate-200 bg-white text-slate-900 shadow-sm hover:shadow-md'
      )}
    >
      {/* Badge */}
      {tier.badge && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2">
          <span className="inline-flex items-center gap-1.5 rounded-full bg-gradient-to-r from-amber-400 to-orange-400 px-3 py-1 text-xs font-bold text-white shadow-sm">
            <Zap size={11} />
            {tier.badge}
          </span>
        </div>
      )}

      {/* Plan name */}
      <div className="mb-2">
        <h3
          className={cn(
            'text-base font-semibold',
            tier.highlighted ? 'text-indigo-100' : 'text-slate-500'
          )}
        >
          {tier.name}
        </h3>
      </div>

      {/* Price */}
      <div className="mb-4">
        {isEnterprise ? (
          <p className="text-4xl font-extrabold tracking-tight">Custom</p>
        ) : (
          <div className="flex items-end gap-1">
            <span className="text-4xl font-extrabold tracking-tight">${price}</span>
            <span
              className={cn(
                'mb-1.5 text-sm',
                tier.highlighted ? 'text-indigo-200' : 'text-slate-400'
              )}
            >
              /mo{yearly && price > 0 ? ' billed yearly' : ''}
            </span>
          </div>
        )}
        <p
          className={cn(
            'mt-2 text-sm',
            tier.highlighted ? 'text-indigo-100' : 'text-slate-500'
          )}
        >
          {tier.description}
        </p>
      </div>

      {/* CTA */}
      <Link
        href={tier.ctaHref}
        id={`pricing-cta-${tier.name.toLowerCase()}`}
        className={cn(
          'mb-8 block rounded-xl py-3 text-center text-sm font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
          tier.highlighted
            ? 'bg-white text-indigo-600 hover:bg-indigo-50 focus-visible:ring-white'
            : 'bg-indigo-600 text-white hover:bg-indigo-700 focus-visible:ring-indigo-600'
        )}
      >
        {tier.cta}
      </Link>

      {/* Feature list */}
      <ul className="flex-1 space-y-3" role="list">
        {tier.features.map((feature) => (
          <li key={feature} className="flex items-start gap-2.5">
            <Check
              size={16}
              className={cn(
                'mt-0.5 flex-shrink-0',
                tier.highlighted ? 'text-indigo-200' : 'text-emerald-500'
              )}
              aria-hidden="true"
            />
            <span
              className={cn(
                'text-sm',
                tier.highlighted ? 'text-indigo-100' : 'text-slate-600'
              )}
            >
              {feature}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
