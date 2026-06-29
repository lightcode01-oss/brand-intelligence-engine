'use client';

import React, { useState, useEffect } from 'react';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { apiClient } from '@/lib/api/client';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Loader2, Sparkles, Shield, Volume2, Globe } from 'lucide-react';

export default function BrandScoreTrends() {
  const workspace = useWorkspaceStore();
  const workspaceId = workspace.activeWorkspace?.id;

  const [loading, setLoading] = useState(true);
  const [bsi, setBsi] = useState(0);
  const [len, setLen] = useState(0);
  const [pron, setPron] = useState(0);
  const [dom, setDom] = useState(0);
  const [tm, setTm] = useState(0);
  const [sem, setSem] = useState(0);
  const [risk, setRisk] = useState<Record<string, number>>({});

  useEffect(() => {
    const fetchTrends = async () => {
      if (!workspaceId) return;
      try {
        const res = await apiClient.get(`/analytics/trends?workspace_id=${workspaceId}`);
        const data = res.data?.data;
        if (data) {
          setBsi(data.average_overall_bsi);
          setLen(data.avg_length);
          setPron(data.avg_pronounceability);
          setDom(data.avg_domain_score);
          setTm(data.avg_trademark_score);
          setSem(data.avg_semantic_score);
          setRisk(data.trademark_risk_distribution || {});
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchTrends();
  }, [workspaceId]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-1">
          <Sparkles className="h-6 w-6 text-indigo-650 animate-pulse" /> Brand Score Trends
        </h1>
        <p className="text-sm text-slate-500 mt-1">Syllable distributions, phonetic pronouncing recall scores, and clearance parameters indicators.</p>
      </div>

      <div className="flex gap-1 border-b border-slate-200 dark:border-slate-800 pb-px">
        <a href="/analytics" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Overview</a>
        <a href="/analytics/credits" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Credits Balance</a>
        <a href="/analytics/usage" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Usage Logs</a>
        <a href="/analytics/team" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Team Activity</a>
        <a href="/analytics/workspace" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Workspace Growth</a>
        <a href="/analytics/ai" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">AI Performance</a>
        <a href="/analytics/trends" className="px-4 py-2 border-b-2 border-indigo-600 text-indigo-600 dark:text-indigo-400 font-semibold text-sm">Score Trends</a>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-20">
          <Loader2 className="h-10 w-10 animate-spin text-indigo-600" />
        </div>
      ) : (
        <div className="space-y-6">
          {/* Main averages columns */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <Card className="hover:shadow-md transition">
              <CardContent className="pt-6">
                <span className="text-xs text-slate-500 font-semibold uppercase">Overall BSI Average</span>
                <p className="text-4xl font-extrabold text-indigo-600 mt-2">{bsi.toFixed(1)}</p>
                <div className="w-full bg-slate-100 dark:bg-slate-800 h-1.5 rounded-full mt-4 overflow-hidden">
                  <div className="bg-indigo-600 h-full rounded-full" style={{ width: `${bsi}%` }} />
                </div>
              </CardContent>
            </Card>

            <Card className="hover:shadow-md transition">
              <CardContent className="pt-6">
                <span className="text-xs text-slate-500 font-semibold uppercase">Avg Brand Name Length</span>
                <p className="text-4xl font-extrabold text-indigo-600 mt-2">{len.toFixed(1)}</p>
                <span className="text-[10px] text-slate-400 block mt-2">Optimal lengths are between 5 to 7 letters.</span>
              </CardContent>
            </Card>

            <Card className="hover:shadow-md transition">
              <CardContent className="pt-6">
                <span className="text-xs text-slate-500 font-semibold uppercase">Pronounceability Score</span>
                <p className="text-4xl font-extrabold text-indigo-600 mt-2">{pron.toFixed(1)}%</p>
                <div className="w-full bg-slate-100 dark:bg-slate-800 h-1.5 rounded-full mt-4 overflow-hidden">
                  <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${pron}%` }} />
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            {/* Clearance indices */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-semibold">Sub-Score Clearance Averages</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="flex items-center gap-1"><Globe className="h-3.5 w-3.5" /> Domain Availability</span>
                    <span className="font-bold">{dom.toFixed(1)}%</span>
                  </div>
                  <div className="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-indigo-600 rounded-full" style={{ width: `${dom}%` }} />
                  </div>
                </div>

                <div className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="flex items-center gap-1"><Shield className="h-3.5 w-3.5" /> Trademark Safety</span>
                    <span className="font-bold">{tm.toFixed(1)}%</span>
                  </div>
                  <div className="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-indigo-600 rounded-full" style={{ width: `${tm}%` }} />
                  </div>
                </div>

                <div className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="flex items-center gap-1"><Volume2 className="h-3.5 w-3.5" /> Phonetic Semantics</span>
                    <span className="font-bold">{sem.toFixed(1)}%</span>
                  </div>
                  <div className="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-indigo-600 rounded-full" style={{ width: `${sem}%` }} />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Trademark Risk Distribution */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-semibold">Clearance Risk Profiles Distribution</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {Object.entries(risk).map(([level, count]) => (
                  <div key={level} className="flex justify-between items-center text-xs">
                    <span className="font-semibold text-slate-700 dark:text-slate-300 capitalize">{level.toLowerCase()} risk</span>
                    <span className="font-bold text-indigo-600">{count} candidates</span>
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
