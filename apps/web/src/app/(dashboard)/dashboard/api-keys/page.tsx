'use client';

import React, { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Key, Plus, Trash2, Calendar, RefreshCw, Copy, Check } from 'lucide-react';

interface ApiKeyItem {
  id: string;
  name: string;
  scopes: string[];
  created_at: string;
  expires_at?: string;
  revoked_at?: string;
  key_prefix: string;
}

export default function ApiKeysPage() {
  const [loading, setLoading] = useState(true);
  const [apiKeys, setApiKeys] = useState<ApiKeyItem[]>([]);
  const [newName, setNewName] = useState('');
  const [scopes, setScopes] = useState<string[]>(['generation.read', 'generation.write']);
  const [expirationDays, setExpirationDays] = useState(30);
  const [createdKey, setCreatedKey] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetchKeys();
  }, []);

  const fetchKeys = async () => {
    try {
      const res = await apiClient.get('/api-keys/');
      setApiKeys(res.data?.data || []);
    } catch {
      // Fail silently
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) return;

    try {
      const res = await apiClient.post('/api-keys/', {
        name: newName,
        scopes: scopes,
        expiration_days: expirationDays
      });
      setCreatedKey(res.data?.data?.raw_key || null);
      setNewName('');
      await fetchKeys();
    } catch {
      alert('Failed to generate new API Key.');
    }
  };

  const handleRevoke = async (id: string) => {
    if (!confirm('Are you sure you want to revoke this API Key immediately?')) return;
    try {
      await apiClient.delete(`/api-keys/${id}`);
      await fetchKeys();
    } catch {
      alert('Failed to revoke API Key.');
    }
  };

  const handleCopy = () => {
    if (createdKey) {
      navigator.clipboard.writeText(createdKey);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <RefreshCw className="h-8 w-8 text-indigo-600 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">API Keys</h1>
        <p className="text-sm text-slate-500">Generate secure API keys to authorize developer requests on Nomen APIs.</p>
      </div>

      {createdKey && (
        <Card className="border-indigo-600 bg-indigo-50 dark:bg-indigo-950/20">
          <CardHeader>
            <CardTitle className="text-sm font-bold text-indigo-900 dark:text-indigo-200">New Key Created Successfully</CardTitle>
            <p className="text-xs text-indigo-700 dark:text-indigo-300">
              Please copy this key now. For security purposes, we will not display it again.
            </p>
          </CardHeader>
          <CardContent className="flex items-center gap-3">
            <code className="flex-1 bg-white dark:bg-slate-800 p-3 rounded border border-indigo-200 font-mono text-xs break-all text-slate-950 dark:text-white">
              {createdKey}
            </code>
            <Button variant="outline" size="sm" onClick={handleCopy} className="flex items-center gap-2">
              {copied ? <Check className="h-4 w-4 text-emerald-600" /> : <Copy className="h-4 w-4" />}
              {copied ? 'Copied' : 'Copy'}
            </Button>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Create Key Card */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-base font-bold">Generate API Key</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-500">Key Name</label>
                <Input
                  type="text"
                  placeholder="e.g. Production Backend"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-500">Expiration Period</label>
                <select
                  value={expirationDays}
                  onChange={(e) => setExpirationDays(Number(e.target.value))}
                  className="w-full text-sm border border-slate-200 dark:border-slate-800 rounded-md p-2 bg-transparent"
                >
                  <option value={30}>30 Days</option>
                  <option value={90}>90 Days</option>
                  <option value={365}>1 Year</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-500">Scopes</label>
                <div className="space-y-2 pt-1">
                  {['generation.read', 'generation.write', 'analytics.read'].map((s) => (
                    <label key={s} className="flex items-center gap-2 text-xs font-semibold">
                      <input
                        type="checkbox"
                        checked={scopes.includes(s)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setScopes([...scopes, s]);
                          } else {
                            setScopes(scopes.filter((item) => item !== s));
                          }
                        }}
                        className="h-4 w-4 text-indigo-600 rounded"
                      />
                      {s}
                    </label>
                  ))}
                </div>
              </div>

              <Button type="submit" variant="primary" className="w-full flex items-center justify-center gap-2">
                <Plus className="h-4 w-4" /> Create Key
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Existing Keys Card */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-base font-bold">Active API Keys</CardTitle>
          </CardHeader>
          <CardContent>
            {apiKeys.length === 0 ? (
              <div className="text-center py-12 text-slate-500">
                <Key className="h-12 w-12 mx-auto mb-3 opacity-30" />
                <p className="text-sm font-semibold">No active API keys found</p>
                <p className="text-xs mt-1">Generate a key to access Nomen services via script.</p>
              </div>
            ) : (
              <div className="divide-y divide-slate-100 dark:divide-slate-800 space-y-4">
                {apiKeys.map((k) => (
                  <div key={k.id} className="flex items-center justify-between pt-4 first:pt-0 gap-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold">{k.name}</span>
                        <code className="text-[10px] bg-slate-100 dark:bg-slate-800 p-0.5 rounded font-mono font-bold text-slate-600">
                          {k.key_prefix}
                        </code>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {k.scopes.map((s) => (
                          <span key={s} className="text-[10px] font-bold text-indigo-600 bg-indigo-50 dark:bg-indigo-950/20 px-1.5 py-0.5 rounded">
                            {s}
                          </span>
                        ))}
                      </div>
                      <div className="flex items-center gap-2 text-[10px] text-slate-500">
                        <Calendar className="h-3.5 w-3.5" />
                        <span>Created: {new Date(k.created_at).toLocaleDateString()}</span>
                        {k.expires_at && (
                          <>
                            <span>•</span>
                            <span>Expires: {new Date(k.expires_at).toLocaleDateString()}</span>
                          </>
                        )}
                      </div>
                    </div>
                    <Button variant="outline" size="sm" onClick={() => handleRevoke(k.id)} className="text-red-500 hover:text-red-700 flex items-center gap-1 border-red-150">
                      <Trash2 className="h-4 w-4" /> Revoke
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
