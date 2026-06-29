'use client';

import React, { useState, useEffect } from 'react';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { apiClient } from '@/lib/api/client';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import {
  Globe, CheckCircle, Loader2, AlertTriangle,
} from 'lucide-react';
import Link from 'next/link';

interface SSOConfig {
  id: string;
  provider: string;
  client_id: string;
  redirect_uri: string;
  is_active: boolean;
}

const PROVIDERS = [
  { id: 'google', name: 'Google Workspace', icon: '🟢', description: 'OAuth2 / OpenID Connect via Google accounts.' },
  { id: 'microsoft', name: 'Microsoft Entra ID', icon: '🔵', description: 'Azure AD / Microsoft 365 enterprise identity.' },
  { id: 'okta', name: 'Okta', icon: '🔷', description: 'Enterprise-grade Okta identity provider.' },
];

export default function SSOConfiguration() {
  const workspace = useWorkspaceStore();
  const workspaceId = workspace.activeWorkspace?.id;

  const [config, setConfig] = useState<SSOConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState('google');
  const [clientId, setClientId] = useState('');
  const [clientSecret, setClientSecret] = useState('');
  const [redirectUri, setRedirectUri] = useState('https://nomen.ai/auth/sso/callback');
  const [domain, setDomain] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    fetchConfig();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [workspaceId]);

  const fetchConfig = async () => {
    if (!workspaceId) return;
    setLoading(true);
    try {
      const res = await apiClient.get('/security/sso/config', {
        headers: { 'X-Workspace-Id': workspaceId },
      });
      const data = res.data?.data;
      if (data && data.id) {
        setConfig(data);
        setSelectedProvider(data.provider);
        setClientId(data.client_id);
        setRedirectUri(data.redirect_uri);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!workspaceId) return;
    setSaving(true);
    setError(null);
    setSuccess(false);
    try {
      await apiClient.post('/security/sso/configure', {
        provider: selectedProvider,
        client_id: clientId,
        client_secret: clientSecret,
        redirect_uri: redirectUri,
        metadata: selectedProvider === 'okta' ? { domain } : {},
      }, {
        headers: { 'X-Workspace-Id': workspaceId },
      });
      setSuccess(true);
      await fetchConfig();
      setClientSecret('');
    } catch {
      setError('Failed to save SSO configuration. Please check your credentials.');
    } finally {
      setSaving(false);
    }
  };

  const SecurityNavTabs = () => (
    <div className="flex gap-1 border-b border-slate-200 dark:border-slate-800 pb-px text-sm">
      {[
        { label: 'Overview', href: '/security' },
        { label: 'MFA', href: '/security/mfa' },
        { label: 'Sessions', href: '/security/sessions' },
        { label: 'Audit Log', href: '/security/audit' },
        { label: 'SSO', href: '/security/sso', active: true },
        { label: 'Privacy', href: '/security/privacy' },
      ].map((tab) => (
        <Link
          key={tab.href}
          href={tab.href}
          className={`px-4 py-2 font-medium transition ${
            tab.active
              ? 'border-b-2 border-indigo-600 text-indigo-600'
              : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
          }`}
        >
          {tab.label}
        </Link>
      ))}
    </div>
  );

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <Globe className="h-6 w-6 text-indigo-600" />
          Single Sign-On (SSO)
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Connect an enterprise identity provider for seamless workspace authentication.
        </p>
      </div>

      <SecurityNavTabs />

      {loading ? (
        <div className="flex justify-center items-center py-20">
          <Loader2 className="h-10 w-10 animate-spin text-indigo-600" />
        </div>
      ) : (
        <div className="space-y-6">
          {/* Current SSO status */}
          {config && (
            <Card className="border-emerald-200 dark:border-emerald-900/20 bg-emerald-50/30 dark:bg-emerald-950/10">
              <CardContent className="pt-4 pb-4 flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-emerald-600" />
                <div>
                  <p className="text-sm font-semibold text-emerald-700 dark:text-emerald-400">
                    SSO Active — {PROVIDERS.find(p => p.id === config.provider)?.name}
                  </p>
                  <p className="text-xs text-slate-500 mt-0.5">Redirect URI: {config.redirect_uri}</p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Provider selection */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-semibold">Select Identity Provider</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {PROVIDERS.map((p) => (
                <button
                  key={p.id}
                  onClick={() => setSelectedProvider(p.id)}
                  className={`w-full flex items-center gap-3 p-3 rounded-xl border transition text-left ${
                    selectedProvider === p.id
                      ? 'border-indigo-400 bg-indigo-50 dark:bg-indigo-950/20'
                      : 'border-slate-200 dark:border-slate-700 hover:border-slate-300'
                  }`}
                >
                  <span className="text-2xl">{p.icon}</span>
                  <div>
                    <p className="text-sm font-semibold text-slate-900 dark:text-white">{p.name}</p>
                    <p className="text-xs text-slate-500">{p.description}</p>
                  </div>
                </button>
              ))}
            </CardContent>
          </Card>

          {/* Configuration form */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-semibold">Provider Configuration</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSave} className="space-y-4">
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase">Client ID</label>
                  <Input
                    placeholder="Enter OAuth2 Client ID"
                    value={clientId}
                    onChange={(e) => setClientId(e.target.value)}
                    required
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase">Client Secret</label>
                  <Input
                    type="password"
                    placeholder="Enter OAuth2 Client Secret (leave blank to keep existing)"
                    value={clientSecret}
                    onChange={(e) => setClientSecret(e.target.value)}
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase">Redirect URI</label>
                  <Input
                    placeholder="https://nomen.ai/auth/sso/callback"
                    value={redirectUri}
                    onChange={(e) => setRedirectUri(e.target.value)}
                    required
                  />
                </div>

                {selectedProvider === 'okta' && (
                  <div className="space-y-1">
                    <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase">Okta Domain</label>
                    <Input
                      placeholder="company.okta.com"
                      value={domain}
                      onChange={(e) => setDomain(e.target.value)}
                    />
                  </div>
                )}

                {error && (
                  <p className="text-sm text-red-500 flex items-center gap-1">
                    <AlertTriangle className="h-4 w-4" /> {error}
                  </p>
                )}
                {success && (
                  <p className="text-sm text-emerald-600 flex items-center gap-1">
                    <CheckCircle className="h-4 w-4" /> SSO configuration saved successfully.
                  </p>
                )}

                <Button type="submit" disabled={saving || !clientId} className="w-full bg-indigo-600 hover:bg-indigo-700 text-white">
                  {saving ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                  Save SSO Configuration
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
