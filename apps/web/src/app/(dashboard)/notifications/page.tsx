'use client';

import React, { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Bell, Check, CheckCheck, Loader2, Sparkles, ShieldAlert, Key } from 'lucide-react';

interface NotificationItem {
  id: string;
  category: string;
  title: string;
  message: string;
  read_at: string | null;
  created_at: string;
}

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [marking, setMarking] = useState(false);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/notifications/');
      setNotifications(res.data?.data || []);
    } catch (err) {
      console.error('Failed to fetch notifications:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();

    const handleNewNotification = (e: Event) => {
      const data = (e as CustomEvent).detail;
      setNotifications((prev) => [data, ...prev]);
    };

    if (typeof window !== 'undefined') {
      window.addEventListener('ws:notification_received', handleNewNotification);
    }
    return () => {
      if (typeof window !== 'undefined') {
        window.removeEventListener('ws:notification_received', handleNewNotification);
      }
    };
  }, []);

  const handleMarkAllRead = async () => {
    setMarking(true);
    try {
      await apiClient.put('/notifications/read-all');
      setNotifications((prev) =>
        prev.map((n) => ({ ...n, read_at: new Date().toISOString() }))
      );
    } catch (err) {
      console.error(err);
    } finally {
      setMarking(false);
    }
  };

  const handleMarkSingleRead = async (id: string) => {
    try {
      await apiClient.put('/notifications/read', [id]);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, read_at: new Date().toISOString() } : n))
      );
    } catch (err) {
      console.error(err);
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'mention':
        return <Sparkles className="h-5 w-5 text-indigo-500" />;
      case 'security':
        return <ShieldAlert className="h-5 w-5 text-red-500" />;
      case 'billing':
        return <Key className="h-5 w-5 text-emerald-500" />;
      default:
        return <Bell className="h-5 w-5 text-slate-500" />;
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Bell className="h-6 w-6 text-indigo-600 animate-bounce" /> Notifications Center
          </h1>
          <p className="text-sm text-slate-500 mt-1">In-app mention alerts, billing logs, and project updates.</p>
        </div>
        {notifications.some((n) => !n.read_at) && (
          <Button 
            onClick={handleMarkAllRead} 
            disabled={marking} 
            variant="outline" 
            size="sm"
            className="flex items-center gap-2"
          >
            {marking ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCheck className="h-4 w-4" />}
            <span>Mark All Read</span>
          </Button>
        )}
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-20">
          <Loader2 className="h-10 w-10 animate-spin text-indigo-600" />
        </div>
      ) : (
        <Card className="shadow-lg border-slate-100 dark:border-slate-800">
          <CardContent className="p-0 divide-y divide-slate-100 dark:divide-slate-800">
            {notifications.length === 0 ? (
              <div className="text-center py-20 text-slate-400">
                You have no notifications at the moment.
              </div>
            ) : (
              notifications.map((n) => (
                <div 
                  key={n.id} 
                  className={`flex gap-4 p-5 hover:bg-slate-50/50 dark:hover:bg-slate-900/10 transition items-start ${!n.read_at ? 'bg-indigo-50/30 dark:bg-indigo-950/5' : ''}`}
                >
                  <div className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800/80">
                    {getCategoryIcon(n.category)}
                  </div>
                  <div className="flex-1 space-y-1">
                    <div className="flex justify-between items-start">
                      <h4 className="font-semibold text-slate-900 dark:text-white">{n.title}</h4>
                      <span className="text-xxs text-slate-400">{new Date(n.created_at).toLocaleDateString()}</span>
                    </div>
                    <p className="text-sm text-slate-600 dark:text-slate-300">{n.message}</p>
                  </div>
                  {!n.read_at && (
                    <button 
                      onClick={() => handleMarkSingleRead(n.id)}
                      className="p-1 rounded-full text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 dark:hover:bg-indigo-950/20 transition"
                      title="Mark as read"
                    >
                      <Check className="h-4 w-4" />
                    </button>
                  )}
                </div>
              ))
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
