import type { Metadata } from 'next';
import React from 'react';
import { Section, SectionHeading } from '@/components/marketing/Section';
import { generateSEO } from '@/lib/seo';
import Link from 'next/link';
import { ArrowRight, Briefcase } from 'lucide-react';

export const metadata: Metadata = generateSEO({
  title: 'Careers',
  description: 'Join Nomen to design the future of brand identity development, scalable data tools, and dynamic AI systems.',
  keywords: ['nomen jobs', 'careers at nomen', 'ai engineer jobs', 'next.js frontend developer position'],
  path: '/careers',
});

const JOBS = [
  {
    title: 'Lead Frontend Engineer',
    department: 'Engineering',
    location: 'Remote (US/EU)',
    type: 'Full-time',
  },
  {
    title: 'Senior Machine Learning (LLM) Engineer',
    department: 'AI & Research',
    location: 'San Francisco, CA (Hybrid)',
    type: 'Full-time',
  },
  {
    title: 'Senior Product Designer',
    department: 'Design',
    location: 'Remote (US)',
    type: 'Full-time',
  },
  {
    title: 'Enterprise Account Executive',
    department: 'Sales & Growth',
    location: 'New York, NY',
    type: 'Full-time',
  },
];

export default function CareersPage() {
  return (
    <Section className="pt-32">
      <SectionHeading
        eyebrow="Work With Us"
        title="Help us build the identity layer of the web"
        description="We are a small, product-focused team of engineers, designers, and researchers building the future of brand creation."
      />

      <div className="mx-auto max-w-3xl mt-12 space-y-6">
        <h2 className="text-xl font-bold text-slate-900 border-b border-slate-200 pb-4">
          Open Positions ({JOBS.length})
        </h2>

        <div className="divide-y divide-slate-100 border border-slate-200 rounded-2xl bg-white overflow-hidden shadow-sm">
          {JOBS.map((job, idx) => (
            <div
              key={idx}
              className="flex flex-col sm:flex-row sm:items-center justify-between p-6 hover:bg-slate-50 transition-colors gap-4"
            >
              <div>
                <h3 className="font-bold text-slate-900 text-base">{job.title}</h3>
                <div className="mt-2 flex items-center gap-3 text-xs text-slate-400 font-medium">
                  <span className="flex items-center gap-1">
                    <Briefcase size={12} />
                    {job.department}
                  </span>
                  <span>•</span>
                  <span>{job.location}</span>
                  <span>•</span>
                  <span>{job.type}</span>
                </div>
              </div>
              <div>
                <Link
                  href="/contact"
                  className="inline-flex h-9 items-center justify-center gap-1.5 rounded-lg border border-slate-200 bg-white px-4 text-xs font-semibold text-slate-700 hover:border-slate-300 transition-colors"
                >
                  Apply
                  <ArrowRight size={12} />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Section>
  );
}
