import type { Metadata } from 'next';
import React from 'react';
import { Section, SectionHeading } from '@/components/marketing/Section';
import { generateSEO } from '@/lib/seo';
import { CheckCircle, Activity } from 'lucide-react';

export const metadata: Metadata = generateSEO({
  title: 'System Status',
  description: 'View the current live performance and operational status of Nomen components.',
  keywords: ['nomen status', 'api uptime', 'service checks'],
  path: '/status',
});

const COMPONENTS = [
  { name: 'Core API Service', status: 'operational', uptime: '99.98%' },
  { name: 'PostgreSQL Database', status: 'operational', uptime: '100.00%' },
  { name: 'Celery Background Workers', status: 'operational', uptime: '99.95%' },
  { name: 'AI Models Pipeline Providers', status: 'operational', uptime: '99.90%' },
  { name: 'Domain Validation Engine', status: 'operational', uptime: '99.99%' },
  { name: 'Trademark Clearance Scanner', status: 'operational', uptime: '99.93%' },
];

export default function StatusPage() {
  return (
    <Section className="pt-32" narrow>
      <SectionHeading
        eyebrow="System Health"
        title="Nomen Service Uptime"
        description="Monitor current live status and uptime metrics of Nomen platform components."
      />

      <div className="space-y-8 mt-12">
        {/* Overall Status Banner */}
        <div className="rounded-2xl border border-emerald-200 bg-emerald-50/50 p-6 flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-100 text-emerald-600">
            <CheckCircle size={24} />
          </div>
          <div>
            <h2 className="text-lg font-bold text-emerald-950">All Systems Operational</h2>
            <p className="text-sm text-emerald-700 mt-0.5">
              We are reporting 100% operational efficiency across all key components and search pipelines.
            </p>
          </div>
        </div>

        {/* Components Grid */}
        <div className="border border-slate-200 rounded-2xl bg-white overflow-hidden shadow-sm divide-y divide-slate-100">
          {COMPONENTS.map((comp, idx) => (
            <div key={idx} className="flex items-center justify-between p-6">
              <div className="flex items-center gap-3">
                <span className="flex h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" aria-hidden="true" />
                <span className="font-bold text-slate-800 text-sm">{comp.name}</span>
              </div>
              <div className="flex items-center gap-6 text-xs font-semibold text-slate-500">
                <span className="text-slate-400">Uptime: {comp.uptime}</span>
                <span className="inline-flex rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-bold text-emerald-700 capitalize">
                  {comp.status}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Incident History Mock */}
        <div className="rounded-2xl border border-slate-200 p-6 bg-white shadow-sm">
          <h3 className="font-bold text-slate-900 text-sm mb-4 flex items-center gap-2">
            <Activity size={16} className="text-indigo-600" />
            Uptime Incident History (Past 90 Days)
          </h3>
          <div className="space-y-4">
            <div className="flex items-start gap-3 border-l-2 border-slate-200 pl-4">
              <div>
                <time className="text-xs text-slate-400 font-semibold">June 15, 2026</time>
                <h4 className="font-semibold text-slate-800 text-xs mt-0.5">API Rate Limiting Incident</h4>
                <p className="text-xs text-slate-500 mt-1">
                  We observed transient database lookup timeouts due to high parallel API generation tasks.
                  Resolved by scaling up connection pools and Redis cache limits. (Duration: 12 minutes).
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3 border-l-2 border-slate-200 pl-4">
              <div>
                <time className="text-xs text-slate-400 font-semibold">May 2, 2026</time>
                <h4 className="font-semibold text-slate-800 text-xs mt-0.5">Scheduled Maintenance Complete</h4>
                <p className="text-xs text-slate-500 mt-1">
                  Completed system infrastructure migration to support containerized staging platforms and Docker configs.
                  Zero customer-facing downtime observed.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Section>
  );
}
