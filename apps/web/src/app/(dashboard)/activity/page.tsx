'use client';

import React, { useState, useEffect } from 'react';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { apiClient } from '@/lib/api/client';
import { Card, CardContent } from '@/components/ui/Card';
import { Activity, Loader2, Sparkles, FolderPlus, UserPlus, FileEdit } from 'lucide-react';

interface ActivityItem {
  id: string;
  action_type: string;
  description: string;
  created_at: string;
  user?: {
    id: string;
    email: string;
  };
}

export default function ActivityPage() {
  const workspace = useWorkspaceStore();
  const workspaceId = workspace.activeWorkspace?.id;

  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchActivities = async () => {
    if (!workspaceId) return;
    setLoading(true);
    try {
      const res = await apiClient.get(`/activity/?workspace_id=${workspaceId}`);
      setActivities(res.data?.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActivities();

    const handleNewActivity = (e: Event) => {
      const data = (e as CustomEvent).detail;
      setActivities((prev) => [data, ...prev]);
    };

    if (typeof window !== 'undefined') {
      window.addEventListener('ws:activity_event', handleNewActivity);
    }
    return () => {
      if (typeof window !== 'undefined') {
        window.removeEventListener('ws:activity_event', handleNewActivity);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [workspaceId]);

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'names_generated':
        return <Sparkles className="h-4 w-4 text-indigo-500" />;
      case 'collection_created':
        return <FolderPlus className="h-4 w-4 text-amber-500" />;
      case 'member_invited':
        return <UserPlus className="h-4 w-4 text-emerald-500" />;
      default:
        return <FileEdit className="h-4 w-4 text-slate-500" />;
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <Activity className="h-6 w-6 text-emerald-500" /> Workspace Activity Feed
        </h1>
        <p className="text-sm text-slate-500 mt-1">Chronological logs of brand discoveries, edits, and team actions.</p>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-20">
          <Loader2 className="h-10 w-10 animate-spin text-indigo-600" />
        </div>
      ) : activities.length === 0 ? (
        <Card className="py-20 text-center text-slate-400">
          <CardContent>No activity events logged in this workspace yet.</CardContent>
        </Card>
      ) : (
        <Card className="shadow-lg border-slate-100 dark:border-slate-800">
          <CardContent className="p-6 relative">
            {/* Timeline Line */}
            <div className="absolute left-[39px] top-6 bottom-6 w-0.5 bg-slate-150 dark:bg-slate-850" />

            <div className="space-y-8 relative">
              {activities.map((act) => (
                <div key={act.id} className="flex items-start gap-4">
                  {/* Icon Circle */}
                  <div className="relative z-10 p-2.5 rounded-full border border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-950 flex items-center justify-center shadow-sm">
                    {getActivityIcon(act.action_type)}
                  </div>
                  {/* Content Bubble */}
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-baseline gap-2">
                      <p className="font-semibold text-sm text-slate-900 dark:text-white">{act.description}</p>
                      <span className="text-xxs text-slate-400 whitespace-nowrap">{new Date(act.created_at).toLocaleTimeString()}</span>
                    </div>
                    {act.user && (
                      <span className="block text-xxs text-slate-400 mt-0.5">Triggered by: {act.user.email}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
