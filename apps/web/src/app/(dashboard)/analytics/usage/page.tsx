'use client';

import React, { useState, useEffect } from 'react';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { apiClient } from '@/lib/api/client';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Loader2 } from 'lucide-react';

interface DailyUsagePoint {
  date: string;
  count: number;
}

export default function UsageAnalytics() {
  const workspace = useWorkspaceStore();
  const workspaceId = workspace.activeWorkspace?.id;

  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [breakdown, setBreakdown] = useState<Record<string, number>>({});
  const [daily, setDaily] = useState<DailyUsagePoint[]>([]);

  useEffect(() => {
    const fetchUsage = async () => {
      if (!workspaceId) return;
      try {
        const res = await apiClient.get(`/analytics/usage?workspace_id=${workspaceId}`);
        const data = res.data?.data;
        if (data) {
          setTotal(data.total_requests);
          setBreakdown(data.provider_breakdown || {});
          setDaily(data.daily_usage || []);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchUsage();
  }, [workspaceId]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Workspace Usage Logs</h1>
        <p className="text-sm text-slate-500 mt-1">Provider requests counts breakdown and API requests volumes tracking.</p>
      </div>

      <div className="flex gap-1 border-b border-slate-200 dark:border-slate-800 pb-px">
        <a href="/analytics" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Overview</a>
        <a href="/analytics/credits" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Credits Balance</a>
        <a href="/analytics/usage" className="px-4 py-2 border-b-2 border-indigo-600 text-indigo-600 dark:text-indigo-400 font-semibold text-sm">Usage Logs</a>
        <a href="/analytics/team" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Team Activity</a>
        <a href="/analytics/workspace" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Workspace Growth</a>
        <a href="/analytics/ai" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">AI Performance</a>
        <a href="/analytics/trends" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Score Trends</a>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-20">
          <Loader2 className="h-10 w-10 animate-spin text-indigo-600" />
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-3">
          {/* Left Column: Metrics summary */}
          <div className="md:col-span-1 space-y-6">
            <Card>
              <CardContent className="pt-6">
                <span className="text-xs text-slate-500 uppercase font-semibold">Workspace Total Jobs Requests</span>
                <p className="text-4xl font-extrabold mt-2 text-slate-900 dark:text-white">{total}</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-semibold">AI Models Distribution</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {Object.keys(breakdown).length === 0 ? (
                  <div className="text-xs text-slate-400">No requests recorded.</div>
                ) : (
                  Object.entries(breakdown).map(([model, count]) => (
                    <div key={model} className="space-y-1">
                      <div className="flex justify-between text-xs font-medium">
                        <span className="text-slate-700 dark:text-slate-300">{model}</span>
                        <span className="text-slate-550">{count} queries</span>
                      </div>
                      <div className="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-indigo-600 rounded-full" 
                          style={{ width: `${(count / total) * 100}%` }}
                        />
                      </div>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>
          </div>

          {/* Right Column: Daily requests list */}
          <div className="md:col-span-2">
            <Card className="h-full">
              <CardHeader>
                <CardTitle className="text-sm font-semibold">Daily Requests Timeline</CardTitle>
              </CardHeader>
              <CardContent className="p-0 divide-y divide-slate-100 dark:divide-slate-800">
                {daily.map((d, i) => (
                  <div key={i} className="flex justify-between items-center p-4">
                    <span className="text-sm font-medium text-slate-700 dark:text-slate-300">{d.date}</span>
                    <span className="font-semibold text-sm text-indigo-600">{d.count} requests</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
