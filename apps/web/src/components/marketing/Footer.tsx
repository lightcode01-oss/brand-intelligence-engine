import React from 'react';
import Link from 'next/link';
import { Zap, Twitter, Github, Linkedin } from 'lucide-react';

const FOOTER_LINKS = {
  Product: [
    { href: '/features', label: 'Features' },
    { href: '/pricing', label: 'Pricing' },
    { href: '/changelog', label: 'Changelog' },
    { href: '/status', label: 'Status' },
  ],
  Company: [
    { href: '/about', label: 'About' },
    { href: '/blog', label: 'Blog' },
    { href: '/careers', label: 'Careers' },
    { href: '/contact', label: 'Contact' },
  ],
  Resources: [
    { href: '/docs', label: 'Documentation' },
    { href: '/faq', label: 'FAQ' },
    { href: '/auth/login', label: 'Sign In' },
    { href: '/auth/register', label: 'Get Started' },
  ],
  Legal: [
    { href: '/privacy', label: 'Privacy Policy' },
    { href: '/terms', label: 'Terms of Service' },
    { href: '/cookies', label: 'Cookie Policy' },
  ],
};

const SOCIALS = [
  { href: 'https://twitter.com/nomenai', label: 'Twitter', icon: Twitter },
  { href: 'https://github.com/lightcode01-oss/brand-intelligence-engine', label: 'GitHub', icon: Github },
  { href: 'https://linkedin.com/company/nomenai', label: 'LinkedIn', icon: Linkedin },
];

export function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white" role="contentinfo">
      <div className="mx-auto max-w-7xl px-6 pt-16 pb-8">
        {/* Top row */}
        <div className="grid grid-cols-2 gap-8 md:grid-cols-5">
          {/* Brand column */}
          <div className="col-span-2 md:col-span-1">
            <Link
              href="/"
              className="flex items-center gap-2.5 font-bold text-xl tracking-tight text-slate-900"
              aria-label="Nomen home"
            >
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-600 to-violet-600">
                <Zap size={16} className="text-white" strokeWidth={2.5} />
              </span>
              Nomen
            </Link>
            <p className="mt-4 text-sm leading-relaxed text-slate-500">
              AI-powered brand intelligence platform for founders and teams who build great products.
            </p>
            <div className="mt-5 flex items-center gap-3">
              {SOCIALS.map(({ href, label, icon: Icon }) => (
                <a
                  key={href}
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={label}
                  className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-slate-500 transition-colors hover:border-slate-300 hover:text-slate-700"
                >
                  <Icon size={16} />
                </a>
              ))}
            </div>
          </div>

          {/* Link columns */}
          {Object.entries(FOOTER_LINKS).map(([category, links]) => (
            <div key={category}>
              <h3 className="mb-4 text-xs font-semibold uppercase tracking-widest text-slate-500">
                {category}
              </h3>
              <ul className="space-y-2.5">
                {links.map(({ href, label }) => (
                  <li key={href}>
                    <Link
                      href={href}
                      className="text-sm text-slate-600 transition-colors hover:text-slate-900"
                    >
                      {label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-slate-200 pt-8 sm:flex-row">
          <p className="text-xs text-slate-400">
            &copy; {new Date().getFullYear()} Nomen, Inc. All rights reserved.
          </p>
          <div className="flex items-center gap-1">
            <span className="inline-flex h-2 w-2 rounded-full bg-emerald-400" aria-hidden="true" />
            <p className="text-xs text-slate-400">All systems operational</p>
          </div>
        </div>
      </div>
    </footer>
  );
}
