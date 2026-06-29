'use client';

import React from 'react';
import Link from 'next/link';
import { ArrowRight, Sparkles } from 'lucide-react';

const ANIMATED_WORDS = ['Powerful', 'Memorable', 'Available', 'Distinctive', 'Legal'];

export function Hero() {
  const [wordIdx, setWordIdx] = React.useState(0);
  const [fade, setFade] = React.useState(true);

  React.useEffect(() => {
    const interval = setInterval(() => {
      setFade(false);
      setTimeout(() => {
        setWordIdx((i) => (i + 1) % ANIMATED_WORDS.length);
        setFade(true);
      }, 300);
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  return (
    <section
      className="relative overflow-hidden bg-white pt-28 pb-20 lg:pt-36 lg:pb-28"
      aria-label="Hero section"
    >
      {/* Background gradient orbs */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -top-40 left-1/2 h-[800px] w-[800px] -translate-x-1/2 rounded-full bg-gradient-radial from-indigo-100/60 via-violet-100/30 to-transparent"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -right-40 top-20 h-[600px] w-[600px] rounded-full bg-gradient-radial from-violet-100/40 via-transparent to-transparent"
      />

      <div className="relative mx-auto max-w-7xl px-6 text-center">
        {/* Eyebrow badge */}
        <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-indigo-200 bg-indigo-50 px-4 py-1.5 text-sm font-medium text-indigo-700">
          <Sparkles size={14} />
          AI-Powered Brand Intelligence Platform
        </div>

        {/* Main headline */}
        <h1 className="mx-auto max-w-4xl text-5xl font-extrabold tracking-tight text-slate-900 sm:text-6xl lg:text-7xl">
          Find brand names that are
          <br />
          <span
            className="inline-block min-w-48 bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent transition-opacity duration-300"
            style={{ opacity: fade ? 1 : 0 }}
            aria-live="polite"
            aria-atomic="true"
          >
            {ANIMATED_WORDS[wordIdx]}
          </span>
        </h1>

        {/* Subheading */}
        <p className="mx-auto mt-6 max-w-2xl text-xl text-slate-500 leading-relaxed">
          Generate AI-powered brand names, validate domains, check trademark availability,
          and score your brand — all in one intelligent pipeline.
        </p>

        {/* CTA buttons */}
        <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
          <Link
            href="/auth/register"
            id="hero-cta-primary"
            className="inline-flex h-12 items-center gap-2 rounded-xl bg-indigo-600 px-8 text-base font-semibold text-white shadow-lg shadow-indigo-200 transition-all hover:bg-indigo-700 hover:shadow-xl hover:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600 focus-visible:ring-offset-2"
          >
            Start for free
            <ArrowRight size={16} />
          </Link>
          <Link
            href="/features"
            id="hero-cta-secondary"
            className="inline-flex h-12 items-center gap-2 rounded-xl border border-slate-200 bg-white px-8 text-base font-semibold text-slate-700 shadow-sm transition-all hover:border-slate-300 hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-400 focus-visible:ring-offset-2"
          >
            See how it works
          </Link>
        </div>

        {/* Social proof */}
        <p className="mt-8 text-sm text-slate-400">
          Free forever • No credit card required • 10 names/month on free plan
        </p>

        {/* Product screenshot placeholder */}
        <div className="relative mx-auto mt-16 max-w-5xl">
          <div className="overflow-hidden rounded-2xl border border-slate-200/80 bg-gradient-to-b from-slate-50 to-white shadow-2xl shadow-slate-200/60">
            <div className="flex items-center gap-1.5 border-b border-slate-200 bg-slate-50 px-4 py-3">
              <span className="h-3 w-3 rounded-full bg-red-400" aria-hidden="true" />
              <span className="h-3 w-3 rounded-full bg-amber-400" aria-hidden="true" />
              <span className="h-3 w-3 rounded-full bg-emerald-400" aria-hidden="true" />
              <div className="ml-4 h-5 w-64 rounded bg-slate-200" aria-hidden="true" />
            </div>
            <div className="p-8">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                {['Brandify', 'Nomixa', 'Vexara'].map((name, i) => (
                  <div
                    key={name}
                    className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
                    aria-hidden="true"
                  >
                    <div className="mb-2 flex items-center justify-between">
                      <span className="font-semibold text-slate-900">{name}</span>
                      <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-medium text-emerald-700">
                        {92 - i * 5}%
                      </span>
                    </div>
                    <div className="space-y-1.5">
                      <div className="flex items-center gap-2 text-xs text-slate-500">
                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                        .com available
                      </div>
                      <div className="flex items-center gap-2 text-xs text-slate-500">
                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                        Low trademark risk
                      </div>
                      <div className="flex items-center gap-2 text-xs text-slate-500">
                        <span className="h-1.5 w-1.5 rounded-full bg-amber-400" />
                        @{name.toLowerCase()} taken
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
          {/* Reflection gradient */}
          <div
            aria-hidden="true"
            className="pointer-events-none absolute -bottom-px inset-x-0 h-20 bg-gradient-to-t from-white"
          />
        </div>
      </div>
    </section>
  );
}
