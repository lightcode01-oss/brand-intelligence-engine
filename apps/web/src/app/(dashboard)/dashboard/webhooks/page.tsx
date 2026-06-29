'use client';

import React, { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Globe, Plus, Trash2, Shield, RefreshCw } from 'lucide-react';

interface WebhookItem {
  id: string;
  url: string;
  secret_key: string;
  events_json: string[];
  is_active: boolean;
}

export default function WebhooksPage() {
  const [loading, setLoading] = useState(true);
  const [webhooks, setWebhooks] = useState<WebhookItem[]>([]);
  const [newUrl, setNewUrl] = useState('');
  const [newSecret, setNewSecret] = useState('');
  const [selectedEvents, setSelectedEvents] = useState<string[]>(['generation.success']);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchWebhooks();
  }, []);

  const fetchWebhooks = async () => {
    try {
      const res = await apiClient.get('/integrations/webhooks');
      setWebhooks(res.data?.data || []);
    } catch {
      // Fail silently
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUrl.trim()) return;

    setSaving(true);
    try {
      const secret = newSecret.trim() || Math.random().toString(36).substring(2, 15);
      await apiClient.post('/integrations/webhooks', {
        url: newUrl,
        secret_key: secret,
        events_json: selectedEvents,
        is_active: true
      });
      setNewUrl('');
      setNewSecret('');
      await fetchWebhooks();
    } catch {
      alert('Failed to register outgoing webhook subscription.');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this webhook subscription?')) return;
    try {
      await apiClient.delete(`/integrations/webhooks/${id}`);
      await fetchWebhooks();
    } catch {
      alert('Failed to delete webhook.');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <RefreshCw className="h-8 w-8 text-indigo-600 animate-spin" />
      </div>
    );
  }

  const eventsList = [
    { key: 'generation.success', label: 'Generation Success', desc: 'Fires when a naming job completes successfully.' },
    { key: 'generation.failed', label: 'Generation Failed', desc: 'Fires when a naming job encounters an error.' },
    { key: 'comment.created', label: 'Comment Created', desc: 'Fires when a team member adds a workspace comment.' }
  ];

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Outbound Webhooks</h1>
        <p className="text-sm text-slate-500">Subscribe to platform events and receive signed payloads to your server endpoints in real-time.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Create Webhook Subscription */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-base font-bold">Add Webhook Endpoint</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-500">Payload URL</label>
                <Input
                  type="url"
                  placeholder="https://api.yourdomain.com/webhooks"
                  value={newUrl}
                  onChange={(e) => setNewUrl(e.target.value)}
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-500">Secret Signature Key</label>
                <Input
                  type="text"
                  placeholder="Leave blank to auto-generate"
                  value={newSecret}
                  onChange={(e) => setNewSecret(e.target.value)}
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-500">Trigger Events</label>
                <div className="space-y-2 pt-1">
                  {eventsList.map((ev) => (
                    <label key={ev.key} className="flex flex-col gap-0.5 cursor-pointer">
                      <div className="flex items-center gap-2 text-xs font-semibold">
                        <input
                          type="checkbox"
                          checked={selectedEvents.includes(ev.key)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedEvents([...selectedEvents, ev.key]);
                            } else {
                              setSelectedEvents(selectedEvents.filter((item) => item !== ev.key));
                            }
                          }}
                          className="h-4 w-4 text-indigo-600 rounded"
                        />
                        {ev.label}
                      </div>
                      <span className="text-[10px] text-slate-400 pl-6">{ev.desc}</span>
                    </label>
                  ))}
                </div>
              </div>

              <Button type="submit" variant="primary" className="w-full flex items-center justify-center gap-2" disabled={saving}>
                <Plus className="h-4 w-4" /> {saving ? 'Adding...' : 'Add Endpoint'}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Existing Webhooks List */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-base font-bold">Registered Webhooks</CardTitle>
          </CardHeader>
          <CardContent>
            {webhooks.length === 0 ? (
              <div className="text-center py-12 text-slate-500">
                <Globe className="h-12 w-12 mx-auto mb-3 opacity-30" />
                <p className="text-sm font-semibold">No registered webhooks found</p>
                <p className="text-xs mt-1">Configure an endpoint to receive real-time updates.</p>
              </div>
            ) : (
              <div className="divide-y divide-slate-100 dark:divide-slate-800 space-y-4">
                {webhooks.map((w) => (
                  <div key={w.id} className="flex items-start justify-between pt-4 first:pt-0 gap-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold break-all">{w.url}</span>
                        <span className="text-[10px] text-emerald-600 bg-emerald-50 dark:bg-emerald-950/20 px-1.5 py-0.5 rounded font-bold">
                          Active
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {w.events_json.map((e) => (
                          <span key={e} className="text-[10px] font-bold text-indigo-600 bg-indigo-50 dark:bg-indigo-950/20 px-1.5 py-0.5 rounded">
                            {e}
                          </span>
                        ))}
                      </div>
                      <div className="flex items-center gap-1.5 text-[10px] text-slate-400 font-mono">
                        <Shield className="h-3.5 w-3.5" />
                        <span>Signing secret: {w.secret_key.substring(0, 8)}...</span>
                      </div>
                    </div>
                    <Button variant="outline" size="sm" onClick={() => handleDelete(w.id)} className="text-red-500 hover:text-red-700 flex items-center gap-1 border-red-150">
                      <Trash2 className="h-4 w-4" /> Delete
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
