'use client';

import React, { useState, useEffect } from 'react';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { apiClient } from '@/lib/api/client';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Loader2, DollarSign, Activity, FileDown, CheckCircle, Brain, RefreshCw } from 'lucide-react';

interface MetricsSummary {
  total_generations: number;
  credits_consumed: number;
  success_rate: number;
  export_count: number;
  active_projects: number;
  total_members: number;
}

interface TimelinePoint {
  date: string;
  count?: number;
  amount?: number;
}

export default function AnalyticsOverview() {
  const workspace = useWorkspaceStore();
  const workspaceId = workspace.activeWorkspace?.id;

  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState<MetricsSummary | null>(null);
  const [dailyGenerations, setDailyGenerations] = useState<TimelinePoint[]>([]);
  const [creditUsage, setCreditUsage] = useState<TimelinePoint[]>([]);

  const fetchAnalytics = async () => {
    if (!workspaceId) return;
    setLoading(true);
    try {
      const res = await apiClient.get(`/analytics/overview?workspace_id=${workspaceId}`);
      const payload = res.data?.data;
      if (payload) {
        setMetrics(payload.metrics);
        setDailyGenerations(payload.daily_generations || []);
        setCreditUsage(payload.credit_usage || []);
      }
    } catch (err) {
      console.error('Failed to load analytics overview:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [workspaceId]);

  // Generate SVG paths for trends line charts
  const getLinePath = (data: TimelinePoint[], key: 'count' | 'amount', width: number, height: number) => {
    if (data.length === 0) return '';
    const maxVal = Math.max(...data.map(d => Number(d[key] || 0)), 1);
    const stepX = width / (data.length - 1);
    
    return data.map((d, i) => {
      const x = i * stepX;
      const y = height - (Number(d[key] || 0) / maxVal) * height;
      return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
    }).join(' ');
  };

  // Generate SVG area paths
  const getAreaPath = (data: TimelinePoint[], key: 'count' | 'amount', width: number, height: number) => {
    const linePath = getLinePath(data, key, width, height);
    if (!linePath) return '';
    return `${linePath} L ${width} ${height} L 0 ${height} Z`;
  };

  return (
    <div className="space-y-6">
      {/* Top Header Section */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-slate-200 dark:border-slate-800 pb-4 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-2 tracking-tight">
            <Activity className="h-8 w-8 text-indigo-600 animate-pulse" /> Workspace Analytics
          </h1>
          <p className="text-sm text-slate-500 mt-1">Real-time overview of generations volumes, credit transactions, and success logs.</p>
        </div>
        
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={fetchAnalytics} disabled={loading} className="flex items-center gap-1">
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Sync Stats</span>
          </Button>
        </div>
      </div>

      {/* Internal Navigation Tabs */}
      <div className="flex flex-wrap gap-1 border-b border-slate-200 dark:border-slate-800 pb-px">
        <a href="/analytics" className="px-4 py-2 border-b-2 border-indigo-600 text-indigo-600 dark:text-indigo-400 font-semibold text-sm">Overview</a>
        <a href="/analytics/credits" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Credits Balance</a>
        <a href="/analytics/usage" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Usage Logs</a>
        <a href="/analytics/team" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Team Activity</a>
        <a href="/analytics/workspace" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Workspace Growth</a>
        <a href="/analytics/ai" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">AI Performance</a>
        <a href="/analytics/trends" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Score Trends</a>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-32">
          <Loader2 className="h-12 w-12 animate-spin text-indigo-600" />
        </div>
      ) : (
        <div className="space-y-6">
          {/* Key Metric cards */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Card className="hover:shadow-md transition">
              <CardContent className="pt-6 flex justify-between items-start">
                <div className="space-y-1">
                  <span className="text-xs text-slate-500 uppercase font-semibold">Total Generations</span>
                  <p className="text-2xl font-bold text-slate-900 dark:text-white">{metrics?.total_generations}</p>
                </div>
                <div className="p-2 bg-indigo-50 dark:bg-indigo-950/20 text-indigo-600 rounded-lg">
                  <Brain className="h-5 w-5" />
                </div>
              </CardContent>
            </Card>

            <Card className="hover:shadow-md transition">
              <CardContent className="pt-6 flex justify-between items-start">
                <div className="space-y-1">
                  <span className="text-xs text-slate-500 uppercase font-semibold">Credits Consumed</span>
                  <p className="text-2xl font-bold text-slate-900 dark:text-white">{metrics?.credits_consumed.toFixed(1)}</p>
                </div>
                <div className="p-2 bg-emerald-50 dark:bg-emerald-950/20 text-emerald-600 rounded-lg">
                  <DollarSign className="h-5 w-5" />
                </div>
              </CardContent>
            </Card>

            <Card className="hover:shadow-md transition">
              <CardContent className="pt-6 flex justify-between items-start">
                <div className="space-y-1">
                  <span className="text-xs text-slate-500 uppercase font-semibold">Pipeline Success Rate</span>
                  <p className="text-2xl font-bold text-slate-900 dark:text-white">{metrics?.success_rate.toFixed(1)}%</p>
                </div>
                <div className="p-2 bg-indigo-50 dark:bg-indigo-950/20 text-indigo-600 rounded-lg">
                  <CheckCircle className="h-5 w-5" />
                </div>
              </CardContent>
            </Card>

            <Card className="hover:shadow-md transition">
              <CardContent className="pt-6 flex justify-between items-start">
                <div className="space-y-1">
                  <span className="text-xs text-slate-500 uppercase font-semibold">Exports Compiled</span>
                  <p className="text-2xl font-bold text-slate-900 dark:text-white">{metrics?.export_count}</p>
                </div>
                <div className="p-2 bg-purple-50 dark:bg-purple-950/20 text-purple-600 rounded-lg">
                  <FileDown className="h-5 w-5" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* SVG Line Charts Row */}
          <div className="grid gap-6 md:grid-cols-2">
            <Card className="border-indigo-100 dark:border-indigo-950/40 bg-white/60 dark:bg-slate-950/60 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-sm font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                  <Brain className="h-4 w-4 text-indigo-600 animate-pulse" /> Daily Generations Volumes
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[220px] w-full relative">
                  <svg className="w-full h-full" viewBox="0 0 500 200" preserveAspectRatio="none">
                    <defs>
                      <linearGradient id="genGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#4F46E5" stopOpacity="0.4" />
                        <stop offset="100%" stopColor="#4F46E5" stopOpacity="0.0" />
                      </linearGradient>
                    </defs>
                    {/* Grid lines */}
                    <line x1="0" y1="50" x2="500" y2="50" stroke="#E2E8F0" strokeWidth="0.5" className="dark:stroke-slate-850" />
                    <line x1="0" y1="100" x2="500" y2="100" stroke="#E2E8F0" strokeWidth="0.5" className="dark:stroke-slate-850" />
                    <line x1="0" y1="150" x2="500" y2="150" stroke="#E2E8F0" strokeWidth="0.5" className="dark:stroke-slate-850" />
                    
                    {/* Area path */}
                    <path d={getAreaPath(dailyGenerations, 'count', 500, 200)} fill="url(#genGrad)" />
                    {/* Line path */}
                    <path d={getLinePath(dailyGenerations, 'count', 500, 200)} fill="none" stroke="#4F46E5" strokeWidth="2.5" />
                  </svg>
                </div>
                <div className="flex justify-between text-[10px] text-slate-400 mt-2 px-1">
                  {dailyGenerations.map((d, i) => (
                    <span key={i}>{d.date.split('-').slice(1).join('/')}</span>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card className="border-indigo-100 dark:border-indigo-950/40 bg-white/60 dark:bg-slate-950/60 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-sm font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                  <DollarSign className="h-4 w-4 text-emerald-600" /> Credit Consumption Trends
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[220px] w-full relative">
                  <svg className="w-full h-full" viewBox="0 0 500 200" preserveAspectRatio="none">
                    <defs>
                      <linearGradient id="credGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#10B981" stopOpacity="0.4" />
                        <stop offset="100%" stopColor="#10B981" stopOpacity="0.0" />
                      </linearGradient>
                    </defs>
                    {/* Grid lines */}
                    <line x1="0" y1="50" x2="500" y2="50" stroke="#E2E8F0" strokeWidth="0.5" className="dark:stroke-slate-850" />
                    <line x1="0" y1="100" x2="500" y2="100" stroke="#E2E8F0" strokeWidth="0.5" className="dark:stroke-slate-850" />
                    <line x1="0" y1="150" x2="500" y2="150" stroke="#E2E8F0" strokeWidth="0.5" className="dark:stroke-slate-850" />
                    
                    {/* Area path */}
                    <path d={getAreaPath(creditUsage, 'amount', 500, 200)} fill="url(#credGrad)" />
                    {/* Line path */}
                    <path d={getLinePath(creditUsage, 'amount', 500, 200)} fill="none" stroke="#10B981" strokeWidth="2.5" />
                  </svg>
                </div>
                <div className="flex justify-between text-[10px] text-slate-400 mt-2 px-1">
                  {creditUsage.map((d, i) => (
                    <span key={i}>{d.date.split('-').slice(1).join('/')}</span>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
