'use client';

import React, { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { Plus, Layout, Zap, Landmark, History, Layers } from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
  const { setActiveWorkspace, setWorkspaces } = useWorkspaceStore();

  // 1. Fetch Workspaces
  const { data: workspacesResponse, isLoading: loadingWorkspaces } = useQuery({
    queryKey: ['workspaces'],
    queryFn: () => apiClient.get('/workspaces/').then((res) => res.data),
  });

  // 2. Fetch Subscription limits
  const { data: subscriptionResponse } = useQuery({
    queryKey: ['subscription'],
    queryFn: () => apiClient.get('/users/me/subscription').then((res) => res.data),
  });

  // 3. Fetch Projects
  const { data: projectsResponse, isLoading: loadingProjects } = useQuery({
    queryKey: ['projects'],
    queryFn: () => apiClient.get('/projects/').then((res) => res.data),
  });

  useEffect(() => {
    if (workspacesResponse?.data?.items) {
      const items = workspacesResponse.data.items;
      setWorkspaces(items);
      if (items.length > 0) {
        setActiveWorkspace(items[0]);
      }
    }
  }, [workspacesResponse, setWorkspaces, setActiveWorkspace]);

  const workspaces = workspacesResponse?.data?.items || [];
  const projects = projectsResponse?.data?.items || [];
  const subTier = subscriptionResponse?.data?.tier || 'FREE';
  const queryCount = subscriptionResponse?.data?.monthly_query_count || 0;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Workspace Overview</h1>
          <p className="text-sm text-slate-500">Overview of brand naming workflows, limits, and team statistics.</p>
        </div>
        <Link href="/dashboard/projects">
          <Button variant="primary" className="flex items-center gap-2">
            <Plus className="h-4 w-4" /> Create New Project
          </Button>
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-6 md:grid-cols-3">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Active Workspace</p>
                <h3 className="mt-1 text-2xl font-bold text-slate-900 dark:text-white">
                  {workspaces[0]?.display_name || 'Personal'}
                </h3>
              </div>
              <div className="rounded-lg bg-indigo-50 p-2 text-indigo-600 dark:bg-indigo-950/20">
                <Layout className="h-6 w-6" />
              </div>
            </div>
            <div className="mt-4 flex items-center justify-between text-xs text-slate-500 border-t border-slate-100 pt-3 dark:border-slate-800">
              <span>Total workspaces:</span>
              <span className="font-semibold text-slate-700 dark:text-slate-300">{workspaces.length || 1} active</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Monthly Usage Queries</p>
                <h3 className="mt-1 text-2xl font-bold text-slate-900 dark:text-white">
                  {queryCount} / 50
                </h3>
              </div>
              <div className="rounded-lg bg-emerald-50 p-2 text-emerald-600 dark:bg-emerald-950/20">
                <Zap className="h-6 w-6" />
              </div>
            </div>
            <div className="mt-4 flex items-center justify-between text-xs text-slate-500 border-t border-slate-100 pt-3 dark:border-slate-800">
              <span>Plan Level:</span>
              <span className="rounded bg-indigo-100 px-2 py-0.5 font-semibold text-indigo-700 dark:bg-indigo-950/40 dark:text-indigo-400">
                {subTier} TIER
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Token Credit Balance</p>
                <h3 className="mt-1 text-2xl font-bold text-slate-900 dark:text-white">
                  140.00
                </h3>
              </div>
              <div className="rounded-lg bg-amber-50 p-2 text-amber-600 dark:bg-amber-950/20">
                <Landmark className="h-6 w-6" />
              </div>
            </div>
            <div className="mt-4 flex items-center justify-between text-xs text-slate-500 border-t border-slate-100 pt-3 dark:border-slate-800">
              <span>Next rollover cycle:</span>
              <span className="font-semibold text-slate-700 dark:text-slate-300">1st of Month</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Dashboard Workspace Details */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Recent Projects */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Layers className="h-5 w-5 text-slate-500" /> Recent Brainstorming Projects
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loadingProjects ? (
              <div className="flex flex-col gap-2">
                <div className="h-8 animate-pulse rounded bg-slate-100 dark:bg-slate-800" />
                <div className="h-8 animate-pulse rounded bg-slate-100 dark:bg-slate-800" />
              </div>
            ) : projects.length === 0 ? (
              <div className="py-6 text-center text-sm text-slate-500">No active projects found. Create one to begin.</div>
            ) : (
              <div className="divide-y divide-slate-100 dark:divide-slate-800">
                {projects.map((proj: { id: string; prompt: string; target_syllables: number }) => (
                  <div key={proj.id} className="flex items-center justify-between py-3">
                    <div>
                      <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                        {proj.prompt.length > 50 ? `${proj.prompt.slice(0, 50)}...` : proj.prompt}
                      </p>
                      <span className="text-xs text-slate-400">Target syllables: {proj.target_syllables}</span>
                    </div>
                    <Link href={`/dashboard/projects/${proj.id}/generate`}>
                      <Button variant="outline" size="sm">Open</Button>
                    </Link>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Activity Log */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <History className="h-5 w-5 text-slate-500" /> Recent Generation Jobs
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loadingWorkspaces ? (
              <div className="h-8 animate-pulse rounded bg-slate-100 dark:bg-slate-800" />
            ) : (
              <div className="space-y-4">
                <div className="flex items-center gap-3 text-sm">
                  <div className="h-2 w-2 rounded-full bg-emerald-500" />
                  <div className="flex-1">
                    <p className="font-semibold text-slate-800 dark:text-slate-200">Asynchronous Job SUCCESS</p>
                    <span className="text-xs text-slate-400">Model: gemini-1.5-flash | Latency: 1500ms</span>
                  </div>
                  <span className="text-xs text-slate-400">Just Now</span>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <div className="h-2 w-2 rounded-full bg-slate-300" />
                  <div className="flex-1">
                    <p className="font-semibold text-slate-800 dark:text-slate-200">Export ZIP compiled</p>
                    <span className="text-xs text-slate-400">Markdown, PDF formats packaged</span>
                  </div>
                  <span className="text-xs text-slate-400">10 mins ago</span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
