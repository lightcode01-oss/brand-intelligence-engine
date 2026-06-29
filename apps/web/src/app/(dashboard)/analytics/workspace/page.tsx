'use client';

import React, { useState, useEffect } from 'react';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { apiClient } from '@/lib/api/client';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Loader2, Layers, Users, Folder, Heart } from 'lucide-react';

interface GrowthPoint {
  date: string;
  projects: number;
  members: number;
}

export default function WorkspaceAnalytics() {
  const workspace = useWorkspaceStore();
  const workspaceId = workspace.activeWorkspace?.id;

  const [loading, setLoading] = useState(true);
  const [projectsCount, setProjectsCount] = useState(0);
  const [membersCount, setMembersCount] = useState(0);
  const [collectionsCount, setCollectionsCount] = useState(0);
  const [favoritesCount, setFavoritesCount] = useState(0);
  const [growth, setGrowth] = useState<GrowthPoint[]>([]);

  useEffect(() => {
    const fetchWorkspaceStats = async () => {
      if (!workspaceId) return;
      try {
        const res = await apiClient.get(`/analytics/workspace?workspace_id=${workspaceId}`);
        const data = res.data?.data;
        if (data) {
          setProjectsCount(data.projects_count);
          setMembersCount(data.members_count);
          setCollectionsCount(data.collections_count);
          setFavoritesCount(data.favorites_count);
          setGrowth(data.growth_timeline || []);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchWorkspaceStats();
  }, [workspaceId]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Workspace growth & Entities metrics</h1>
        <p className="text-sm text-slate-500 mt-1">Timeline measurements of projects and folder structures creations inside the active workspace.</p>
      </div>

      <div className="flex gap-1 border-b border-slate-200 dark:border-slate-800 pb-px">
        <a href="/analytics" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Overview</a>
        <a href="/analytics/credits" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Credits Balance</a>
        <a href="/analytics/usage" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Usage Logs</a>
        <a href="/analytics/team" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Team Activity</a>
        <a href="/analytics/workspace" className="px-4 py-2 border-b-2 border-indigo-600 text-indigo-600 dark:text-indigo-400 font-semibold text-sm">Workspace Growth</a>
        <a href="/analytics/ai" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">AI Performance</a>
        <a href="/analytics/trends" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Score Trends</a>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-20">
          <Loader2 className="h-10 w-10 animate-spin text-indigo-600" />
        </div>
      ) : (
        <div className="space-y-6">
          {/* Key Metrics cards */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardContent className="pt-6 flex justify-between items-center">
                <div>
                  <span className="text-xs text-slate-500 uppercase font-semibold">Campaign Projects</span>
                  <p className="text-2xl font-bold mt-1 text-slate-900 dark:text-white">{projectsCount}</p>
                </div>
                <div className="p-2 rounded bg-indigo-50 text-indigo-600 dark:bg-indigo-950/20">
                  <Layers className="h-5 w-5" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6 flex justify-between items-center">
                <div>
                  <span className="text-xs text-slate-500 uppercase font-semibold">Active Members</span>
                  <p className="text-2xl font-bold mt-1 text-slate-900 dark:text-white">{membersCount}</p>
                </div>
                <div className="p-2 rounded bg-emerald-50 text-emerald-600 dark:bg-emerald-950/20">
                  <Users className="h-5 w-5" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6 flex justify-between items-center">
                <div>
                  <span className="text-xs text-slate-500 uppercase font-semibold">Collections Folders</span>
                  <p className="text-2xl font-bold mt-1 text-slate-900 dark:text-white">{collectionsCount}</p>
                </div>
                <div className="p-2 rounded bg-amber-50 text-amber-500 dark:bg-amber-950/20">
                  <Folder className="h-5 w-5" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6 flex justify-between items-center">
                <div>
                  <span className="text-xs text-slate-500 uppercase font-semibold">Starred Favorites</span>
                  <p className="text-2xl font-bold mt-1 text-slate-900 dark:text-white">{favoritesCount}</p>
                </div>
                <div className="p-2 rounded bg-red-50 text-red-500 dark:bg-red-950/20">
                  <Heart className="h-5 w-5" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Growth Timeline list */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-semibold">Workspace Timeline Growth Index</CardTitle>
            </CardHeader>
            <CardContent className="p-0 divide-y divide-slate-100 dark:divide-slate-800">
              {growth.map((g, i) => (
                <div key={i} className="flex justify-between items-center p-4">
                  <span className="text-sm font-medium text-slate-700 dark:text-slate-300">{g.date}</span>
                  <div className="flex gap-4 text-xs font-semibold">
                    <span className="text-indigo-600">{g.projects} Projects</span>
                    <span className="text-slate-500">{g.members} Members</span>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
