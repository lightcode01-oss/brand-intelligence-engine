import React from 'react';

const STATS = [
  { value: '50K+', label: 'Brand names generated', suffix: '' },
  { value: '12K+', label: 'Founders served', suffix: '' },
  { value: '98%', label: 'Accuracy on trademark risk', suffix: '' },
  { value: '<2s', label: 'Average generation time', suffix: '' },
];

export function Stats() {
  return (
    <section className="border-y border-slate-200 bg-slate-50 py-14" aria-label="Platform statistics">
      <div className="mx-auto max-w-7xl px-6">
        <dl className="grid grid-cols-2 gap-8 md:grid-cols-4">
          {STATS.map(({ value, label }) => (
            <div key={label} className="text-center">
              <dt className="text-sm font-medium text-slate-500">{label}</dt>
              <dd className="mt-2 text-4xl font-extrabold tracking-tight text-slate-900">
                {value}
              </dd>
            </div>
          ))}
        </dl>
      </div>
    </section>
  );
}
