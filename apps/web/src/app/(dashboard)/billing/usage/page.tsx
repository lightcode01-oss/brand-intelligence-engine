'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { BarChart3, Zap, Download, Globe, AlertTriangle, CheckCircle } from 'lucide-react';

interface ActionUsage {
  used: number;
  limit: number;
  unlimited: boolean;
  remaining: number | null;
  percent: number;
}

interface UsageSummary {
  period_start: string;
  tier: string;
  actions: {
    generation: ActionUsage;
    export: ActionUsage;
    api_request: ActionUsage;
  };
}

function UsageBar({
  label,
  icon: Icon,
  usage,
  color,
}: {
  label: string;
  icon: React.ElementType;
  usage: ActionUsage;
  color: string;
}) {
  const pct = usage.unlimited ? 0 : Math.min(usage.percent, 100);
  const isNearLimit = pct >= 80 && !usage.unlimited;
  const isAtLimit = pct >= 100 && !usage.unlimited;

  const barColor = isAtLimit
    ? 'bg-red-500'
    : isNearLimit
    ? 'bg-amber-500'
    : color;

  return (
    <div className="space-y-3 rounded-2xl border border-white/5 bg-white/5 p-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div
            className={`flex h-9 w-9 items-center justify-center rounded-xl ${
              isAtLimit
                ? 'bg-red-500/10'
                : isNearLimit
                ? 'bg-amber-500/10'
                : 'bg-violet-500/10'
            }`}
          >
            <Icon
              size={18}
              className={
                isAtLimit
                  ? 'text-red-400'
                  : isNearLimit
                  ? 'text-amber-400'
                  : 'text-violet-400'
              }
            />
          </div>
          <div>
            <p className="text-sm font-medium text-white">{label}</p>
            {isAtLimit && (
              <p className="text-xs text-red-400 flex items-center gap-1 mt-0.5">
                <AlertTriangle size={10} />
                Quota exceeded
              </p>
            )}
            {isNearLimit && !isAtLimit && (
              <p className="text-xs text-amber-400 flex items-center gap-1 mt-0.5">
                <AlertTriangle size={10} />
                Approaching limit
              </p>
            )}
          </div>
        </div>
        <div className="text-right">
          {usage.unlimited ? (
            <span className="rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs font-medium text-emerald-400 border border-emerald-500/20">
              Unlimited
            </span>
          ) : (
            <div>
              <p className="text-sm font-bold text-white">
                {usage.used.toLocaleString()}{' '}
                <span className="text-xs font-normal text-muted">
                  / {usage.limit.toLocaleString()}
                </span>
              </p>
              {usage.remaining !== null && (
                <p className="text-xs text-muted mt-0.5">
                  {usage.remaining.toLocaleString()} remaining
                </p>
              )}
            </div>
          )}
        </div>
      </div>

      {!usage.unlimited && (
        <div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-white/5">
            <div
              className={`h-full rounded-full transition-all duration-700 ${barColor}`}
              style={{ width: `${pct}%` }}
            />
          </div>
          <p className="mt-1.5 text-right text-xs text-muted">{pct.toFixed(1)}% used</p>
        </div>
      )}
    </div>
  );
}

function formatDate(iso: string) {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(new Date(iso));
}

const TIER_LABELS: Record<string, string> = {
  free: 'Free',
  starter: 'Starter',
  pro: 'Pro',
  business: 'Business',
  enterprise: 'Enterprise',
};

export default function UsagePage() {
  const { data: usageResponse, isLoading, error } = useQuery({
    queryKey: ['billing-usage'],
    queryFn: () => apiClient.get('/billing/usage').then((res) => res.data),
  });

  const usage: UsageSummary | undefined = usageResponse?.data;

  return (
    <div className="space-y-8">
      {/* Page header */}
      <div>
        <h1 className="text-3xl font-bold text-white tracking-tight">Usage Dashboard</h1>
        <p className="text-muted mt-1">
          Monitor your consumption across all metered resources.
        </p>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-28 animate-pulse rounded-2xl bg-white/5" />
          ))}
        </div>
      ) : error || !usage ? (
        <div className="rounded-2xl border border-red-500/20 bg-red-500/10 p-10 text-center">
          <AlertTriangle size={36} className="mx-auto mb-3 text-red-400" />
          <p className="text-sm text-red-400">Failed to load usage data. Please try again.</p>
        </div>
      ) : (
        <>
          {/* Billing period info */}
          <Card>
            <CardContent className="pt-5 pb-5">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-xs text-muted uppercase tracking-wide">Billing Period</p>
                  <p className="mt-0.5 text-sm font-semibold text-white">
                    Started {formatDate(usage.period_start)}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted">Current Plan:</span>
                  <span className="rounded-full bg-violet-500/15 px-3 py-1 text-xs font-semibold text-violet-300 border border-violet-500/20">
                    {TIER_LABELS[usage.tier] ?? usage.tier}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Usage bars */}
          <div>
            <h2 className="mb-4 text-sm font-semibold text-muted uppercase tracking-wide">
              Resource Consumption
            </h2>
            <div className="space-y-4">
              <UsageBar
                label="AI Generations"
                icon={Zap}
                usage={usage.actions.generation}
                color="bg-violet-500"
              />
              <UsageBar
                label="Exports"
                icon={Download}
                usage={usage.actions.export}
                color="bg-cyan-500"
              />
              <UsageBar
                label="API Requests"
                icon={Globe}
                usage={usage.actions.api_request}
                color="bg-indigo-500"
              />
            </div>
          </div>

          {/* Upgrade prompt if any quota is near/at limit */}
          {Object.values(usage.actions).some((a) => a.percent >= 80 && !a.unlimited) && (
            <div className="rounded-2xl border border-amber-500/20 bg-amber-500/5 p-6">
              <div className="flex items-start gap-4">
                <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-amber-500/10">
                  <AlertTriangle size={20} className="text-amber-400" />
                </div>
                <div className="flex-1">
                  <p className="font-semibold text-amber-300">Approaching quota limits</p>
                  <p className="mt-1 text-sm text-muted">
                    One or more resources are near their monthly limit. Upgrade your plan to
                    avoid interruptions.
                  </p>
                  <a
                    href="/billing"
                    className="mt-3 inline-flex items-center gap-1.5 rounded-lg bg-amber-500 px-4 py-2 text-xs font-semibold text-black transition-all hover:bg-amber-400"
                  >
                    View Plans
                  </a>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
