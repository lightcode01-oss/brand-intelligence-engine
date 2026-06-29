'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as zod from 'zod';
import { Mail, ArrowRight, CheckCircle } from 'lucide-react';

const schema = zod.object({
  email: zod.string().email('Please enter a valid email address.'),
});

type FormData = zod.infer<typeof schema>;

interface NewsletterProps {
  title?: string;
  description?: string;
  compact?: boolean;
}

export function Newsletter({
  title = 'Stay in the loop',
  description = 'Get the latest on AI brand intelligence, naming strategies, and product updates — delivered monthly.',
  compact = false,
}: NewsletterProps) {
  const [submitted, setSubmitted] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  const onSubmit = async ({ email }: FormData) => {
    setServerError(null);
    try {
      const res = await fetch('/api/newsletter/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      const data = await res.json();
      if (data.success) {
        setSubmitted(true);
      } else {
        setServerError(data.message || 'Subscription failed. Please try again.');
      }
    } catch {
      setServerError('Network error. Please try again.');
    }
  };

  if (submitted) {
    return (
      <div className="flex flex-col items-center gap-3 text-center">
        <CheckCircle size={40} className="text-emerald-500" aria-hidden="true" />
        <p className="text-base font-semibold text-slate-900">
          You&apos;re subscribed!
        </p>
        <p className="text-sm text-slate-500">Welcome to the Nomen community.</p>
      </div>
    );
  }

  if (compact) {
    return (
      <form onSubmit={handleSubmit(onSubmit)} noValidate aria-label="Newsletter signup">
        <div className="flex gap-2">
          <label htmlFor="newsletter-email-compact" className="sr-only">
            Email address
          </label>
          <input
            id="newsletter-email-compact"
            type="email"
            placeholder="your@email.com"
            autoComplete="email"
            className="h-10 flex-1 rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-900 placeholder-slate-400 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            {...register('email')}
          />
          <button
            type="submit"
            disabled={isSubmitting}
            className="inline-flex h-10 items-center gap-1.5 rounded-lg bg-indigo-600 px-4 text-sm font-semibold text-white transition-all hover:bg-indigo-700 disabled:opacity-60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600 focus-visible:ring-offset-2"
          >
            {isSubmitting ? (
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" aria-hidden="true" />
            ) : (
              <ArrowRight size={14} />
            )}
            Subscribe
          </button>
        </div>
        {errors.email && (
          <p className="mt-1.5 text-xs text-red-500" role="alert">
            {errors.email.message}
          </p>
        )}
        {serverError && (
          <p className="mt-1.5 text-xs text-red-500" role="alert">
            {serverError}
          </p>
        )}
      </form>
    );
  }

  return (
    <section
      className="bg-indigo-50 py-16"
      aria-labelledby="newsletter-heading"
    >
      <div className="mx-auto max-w-2xl px-6 text-center">
        <div className="mb-4 flex justify-center">
          <span className="flex h-12 w-12 items-center justify-center rounded-full bg-indigo-100">
            <Mail size={22} className="text-indigo-600" aria-hidden="true" />
          </span>
        </div>
        <h2 id="newsletter-heading" className="text-2xl font-bold text-slate-900">
          {title}
        </h2>
        <p className="mt-3 text-slate-500">{description}</p>

        <form
          onSubmit={handleSubmit(onSubmit)}
          noValidate
          className="mt-6"
          aria-label="Newsletter signup"
        >
          <div className="flex flex-col gap-3 sm:flex-row">
            <label htmlFor="newsletter-email" className="sr-only">
              Email address
            </label>
            <input
              id="newsletter-email"
              type="email"
              placeholder="your@email.com"
              autoComplete="email"
              className="h-11 flex-1 rounded-xl border border-slate-200 bg-white px-4 text-sm text-slate-900 placeholder-slate-400 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
              {...register('email')}
            />
            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex h-11 items-center justify-center gap-2 rounded-xl bg-indigo-600 px-6 text-sm font-semibold text-white shadow-sm transition-all hover:bg-indigo-700 disabled:opacity-60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600 focus-visible:ring-offset-2"
            >
              {isSubmitting ? (
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" aria-hidden="true" />
              ) : null}
              Subscribe
            </button>
          </div>
          {errors.email && (
            <p className="mt-2 text-xs text-red-500 text-left" role="alert">
              {errors.email.message}
            </p>
          )}
          {serverError && (
            <p className="mt-2 text-xs text-red-500" role="alert">
              {serverError}
            </p>
          )}
          <p className="mt-3 text-xs text-slate-400">
            No spam. Unsubscribe any time. We respect your privacy.
          </p>
        </form>
      </div>
    </section>
  );
}
