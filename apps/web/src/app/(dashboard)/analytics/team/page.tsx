'use client';

import React, { useState, useEffect } from 'react';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { apiClient } from '@/lib/api/client';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Loader2, Users, Trophy } from 'lucide-react';

interface MemberActivity {
  user_id: string;
  email: string;
  credits_consumed: number;
  generations_count: number;
  exports_count: number;
  comments_count: number;
  favorites_count: number;
  collections_count: number;
}

interface LeaderboardRow {
  email: string;
  score: number;
}

export default function TeamActivity() {
  const workspace = useWorkspaceStore();
  const workspaceId = workspace.activeWorkspace?.id;

  const [loading, setLoading] = useState(true);
  const [members, setMembers] = useState<MemberActivity[]>([]);
  const [leaderboard, setLeaderboard] = useState<LeaderboardRow[]>([]);

  useEffect(() => {
    const fetchTeam = async () => {
      if (!workspaceId) return;
      try {
        const res = await apiClient.get(`/analytics/team?workspace_id=${workspaceId}`);
        const data = res.data?.data;
        if (data) {
          setMembers(data.members || []);
          setLeaderboard(data.leaderboard || []);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchTeam();
  }, [workspaceId]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Team Activity & Leaderboard</h1>
        <p className="text-sm text-slate-500 mt-1">Audit user-level generations counts, exports, commentary logs, and workspace actions.</p>
      </div>

      <div className="flex gap-1 border-b border-slate-200 dark:border-slate-800 pb-px">
        <a href="/analytics" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Overview</a>
        <a href="/analytics/credits" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Credits Balance</a>
        <a href="/analytics/usage" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Usage Logs</a>
        <a href="/analytics/team" className="px-4 py-2 border-b-2 border-indigo-600 text-indigo-600 dark:text-indigo-400 font-semibold text-sm">Team Activity</a>
        <a href="/analytics/workspace" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Workspace Growth</a>
        <a href="/analytics/ai" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">AI Performance</a>
        <a href="/analytics/trends" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Score Trends</a>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-20">
          <Loader2 className="h-10 w-10 animate-spin text-indigo-600" />
        </div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Members Table */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-semibold flex items-center gap-1.5">
                  <Users className="h-4 w-4 text-indigo-600" /> Workspace Team Activity Index
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0 overflow-x-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/10 text-slate-500 uppercase font-semibold">
                      <th className="p-4">Email</th>
                      <th className="p-4 text-center">Generations</th>
                      <th className="p-4 text-center">Exports</th>
                      <th className="p-4 text-center">Comments</th>
                      <th className="p-4 text-center">Favorites</th>
                      <th className="p-4 text-center">Credits</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                    {members.map((m) => (
                      <tr key={m.user_id} className="hover:bg-slate-50/30 dark:hover:bg-slate-900/5 transition">
                        <td className="p-4 font-medium text-slate-800 dark:text-slate-200">{m.email}</td>
                        <td className="p-4 text-center font-bold text-indigo-600">{m.generations_count}</td>
                        <td className="p-4 text-center">{m.exports_count}</td>
                        <td className="p-4 text-center">{m.comments_count}</td>
                        <td className="p-4 text-center">{m.favorites_count}</td>
                        <td className="p-4 text-center font-semibold text-emerald-600">{m.credits_consumed.toFixed(1)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </CardContent>
            </Card>
          </div>

          {/* Leaderboard Column */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-semibold flex items-center gap-1.5">
                  <Trophy className="h-4 w-4 text-amber-500 fill-amber-500/10" /> Workspace Leaderboard
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {leaderboard.map((lead, i) => (
                  <div key={i} className="flex justify-between items-center p-3 rounded-xl border border-slate-100 dark:border-slate-850 bg-slate-50/20 dark:bg-slate-900/5">
                    <div className="flex items-center gap-3">
                      <span className="h-6 w-6 rounded-full bg-indigo-50 dark:bg-indigo-950/20 text-indigo-600 text-xxs font-bold flex items-center justify-center">
                        {i + 1}
                      </span>
                      <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">{lead.email.split('@')[0]}</span>
                    </div>
                    <span className="text-xs font-bold text-indigo-600">{lead.score} pts</span>
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
