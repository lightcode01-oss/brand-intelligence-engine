import React from 'react';

const LOGOS = [
  { name: 'Y Combinator', abbr: 'YC' },
  { name: 'Sequoia', abbr: 'SEQ' },
  { name: 'Product Hunt', abbr: 'PH' },
  { name: 'Stripe Atlas', abbr: 'SA' },
  { name: 'AngelList', abbr: 'AL' },
  { name: 'Hacker News', abbr: 'HN' },
];

export function LogoCloud() {
  return (
    <section className="py-12" aria-label="Trusted by community">
      <div className="mx-auto max-w-7xl px-6">
        <p className="mb-8 text-center text-sm font-medium text-slate-400">
          Trusted by founders from top communities and accelerators
        </p>
        <div className="flex flex-wrap items-center justify-center gap-8 opacity-50 grayscale">
          {LOGOS.map(({ name, abbr }) => (
            <div
              key={name}
              className="flex h-10 min-w-[80px] items-center justify-center rounded-lg border border-slate-200 bg-white px-4 text-sm font-bold text-slate-400 shadow-sm"
              title={name}
              aria-label={name}
            >
              {abbr}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
