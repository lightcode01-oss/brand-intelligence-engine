'use client';

import React, { useState, useEffect } from 'react';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { apiClient } from '@/lib/api/client';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Loader2, Zap, Hourglass, ShieldAlert, Cpu } from 'lucide-react';

interface AIProviderMetric {
  provider: string;
  latency_avg_ms: number;
  success_rate: number;
  failure_rate: number;
  requests_total: number;
  cost_total: number;
  tokens_avg: number;
  requests_per_minute: number;
}

export default function AIPerformance() {
  const workspace = useWorkspaceStore();
  const workspaceId = workspace.activeWorkspace?.id;

  const [loading, setLoading] = useState(true);
  const [providers, setProviders] = useState<AIProviderMetric[]>([]);

  useEffect(() => {
    const fetchAIStats = async () => {
      if (!workspaceId) return;
      try {
        const res = await apiClient.get(`/analytics/ai-performance?workspace_id=${workspaceId}`);
        const data = res.data?.data;
        if (data) {
          setProviders(data.providers || []);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchAIStats();
  }, [workspaceId]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">AI Provider Telemetry & Latencies</h1>
        <p className="text-sm text-slate-500 mt-1">Real-time health dashboard tracking latency milliseconds, success rates, and cost budgets per provider.</p>
      </div>

      <div className="flex gap-1 border-b border-slate-200 dark:border-slate-800 pb-px">
        <a href="/analytics" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Overview</a>
        <a href="/analytics/credits" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Credits Balance</a>
        <a href="/analytics/usage" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Usage Logs</a>
        <a href="/analytics/team" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Team Activity</a>
        <a href="/analytics/workspace" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Workspace Growth</a>
        <a href="/analytics/ai" className="px-4 py-2 border-b-2 border-indigo-600 text-indigo-600 dark:text-indigo-400 font-semibold text-sm">AI Performance</a>
        <a href="/analytics/trends" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Score Trends</a>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-20">
          <Loader2 className="h-10 w-10 animate-spin text-indigo-600" />
        </div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {providers.map((p) => (
            <Card key={p.provider} className="border-indigo-150 dark:border-indigo-950/20 shadow hover:shadow-md transition">
              <CardHeader className="flex flex-row items-center justify-between pb-2 border-b border-slate-100 dark:border-slate-800">
                <CardTitle className="text-sm font-bold flex items-center gap-1.5 uppercase">
                  <Cpu className="h-4 w-4 text-indigo-600" /> {p.provider.split('-')[0]}
                </CardTitle>
                <span className="text-[10px] text-slate-400 capitalize">{p.provider}</span>
              </CardHeader>
              <CardContent className="pt-4 space-y-4 text-xs">
                {/* Average Latency */}
                <div className="flex justify-between">
                  <span className="text-slate-500 flex items-center gap-1"><Hourglass className="h-3.5 w-3.5" /> Latency Avg</span>
                  <span className="font-bold text-slate-800 dark:text-slate-200">{p.latency_avg_ms.toFixed(0)} ms</span>
                </div>

                {/* Success Rate */}
                <div className="flex justify-between">
                  <span className="text-slate-500 flex items-center gap-1"><Zap className="h-3.5 w-3.5 text-indigo-600" /> Success Rate</span>
                  <span className="font-bold text-emerald-600">{p.success_rate.toFixed(1)}%</span>
                </div>

                {/* Failures Rate */}
                <div className="flex justify-between">
                  <span className="text-slate-500 flex items-center gap-1"><ShieldAlert className="h-3.5 w-3.5 text-red-500" /> Failure Rate</span>
                  <span className="font-bold text-red-500">{p.failure_rate.toFixed(1)}%</span>
                </div>

                {/* Cost spent */}
                <div className="flex justify-between">
                  <span className="text-slate-500">Cumulative Cost</span>
                  <span className="font-bold text-slate-800 dark:text-slate-200">${p.cost_total.toFixed(4)}</span>
                </div>

                {/* Average token size */}
                <div className="flex justify-between">
                  <span className="text-slate-500">Avg Tokens/Req</span>
                  <span className="font-bold text-slate-850 dark:text-slate-350">{p.tokens_avg.toFixed(0)} tokens</span>
                </div>

                {/* Total Requests count */}
                <div className="flex justify-between pt-2 border-t border-slate-100 dark:border-slate-850 font-bold">
                  <span className="text-slate-700 dark:text-slate-350">Total requests</span>
                  <span className="text-indigo-600">{p.requests_total} requests</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
