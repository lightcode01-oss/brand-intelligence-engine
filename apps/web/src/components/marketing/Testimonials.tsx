import React from 'react';
import { Star } from 'lucide-react';

const TESTIMONIALS = [
  {
    quote:
      "Nomen saved us weeks of naming workshops and legal back-and-forth. We went from idea to registered trademark in 3 days.",
    author: 'Sarah Chen',
    title: 'Co-founder, Loopify',
    avatar: 'SC',
  },
  {
    quote:
      "The trademark risk scoring alone is worth every cent. We avoided a $40K rebrand by catching a conflict before launch.",
    author: 'Marcus Reeves',
    title: 'CEO, Vaultify',
    avatar: 'MR',
  },
  {
    quote:
      "As a solo founder, I can't afford an agency. Nomen gave me agency-quality brand discovery at a price I could actually afford.",
    author: 'Priya Anand',
    title: 'Founder, Stackr',
    avatar: 'PA',
  },
  {
    quote:
      "We ran 6 naming rounds in 2 hours. The brand score helped our team align on a winner without the usual politics.",
    author: 'Tom Fischer',
    title: 'VP Product, Nexlify',
    avatar: 'TF',
  },
  {
    quote:
      "Domain availability + social handle check + trademark risk all in one tool. I don't know how we managed without it.",
    author: 'Aiko Tanaka',
    title: 'Founder, Kaiflow',
    avatar: 'AT',
  },
  {
    quote:
      "Our investors asked us how we found such a clean, available name so quickly. The answer was Nomen.",
    author: 'Luis Guerrero',
    title: 'Co-founder, Clarifai Studio',
    avatar: 'LG',
  },
];

function Stars() {
  return (
    <div className="flex gap-0.5" aria-label="5 out of 5 stars">
      {[...Array(5)].map((_, i) => (
        <Star key={i} size={14} className="fill-amber-400 text-amber-400" aria-hidden="true" />
      ))}
    </div>
  );
}

function Avatar({ initials }: { initials: string }) {
  return (
    <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 text-sm font-semibold text-white">
      {initials}
    </div>
  );
}

export function Testimonials() {
  return (
    <section
      className="bg-slate-50 py-20 lg:py-28"
      aria-labelledby="testimonials-heading"
    >
      <div className="mx-auto max-w-7xl px-6">
        <div className="mb-14 text-center">
          <p className="mb-3 text-sm font-semibold uppercase tracking-widest text-indigo-600">
            Customer Stories
          </p>
          <h2
            id="testimonials-heading"
            className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl"
          >
            Trusted by founders worldwide
          </h2>
          <p className="mx-auto mt-5 max-w-xl text-lg text-slate-500">
            Join thousands of founders who&apos;ve discovered their perfect brand name with Nomen.
          </p>
        </div>

        <div className="columns-1 gap-6 sm:columns-2 lg:columns-3">
          {TESTIMONIALS.map(({ quote, author, title, avatar }) => (
            <blockquote
              key={author}
              className="mb-6 break-inside-avoid rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
            >
              <Stars />
              <p className="mt-4 text-sm leading-relaxed text-slate-700">&ldquo;{quote}&rdquo;</p>
              <footer className="mt-5 flex items-center gap-3">
                <Avatar initials={avatar} />
                <div>
                  <cite className="not-italic text-sm font-semibold text-slate-900">
                    {author}
                  </cite>
                  <p className="text-xs text-slate-500">{title}</p>
                </div>
              </footer>
            </blockquote>
          ))}
        </div>
      </div>
    </section>
  );
}
