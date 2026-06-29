'use client';

import React, { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Slack, MessageSquare, Shield, Activity, RefreshCw } from 'lucide-react';

interface Integration {
  id?: string;
  provider_slug: string;
  settings_json: Record<string, string>;
  is_active: boolean;
}

export default function IntegrationsPage() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState<string | null>(null);
  const [testing, setTesting] = useState<string | null>(null);
  const [integrations, setIntegrations] = useState<Integration[]>([]);

  // State to hold settings and active values for each provider slug
  const [formSettings, setFormSettings] = useState<Record<string, Record<string, string>>>({});
  const [formActive, setFormActive] = useState<Record<string, boolean>>({});

  useEffect(() => {
    fetchIntegrations();
  }, []);

  const fetchIntegrations = async () => {
    try {
      const res = await apiClient.get('/integrations/');
      const items: Integration[] = res.data?.data || [];
      setIntegrations(items);

      // Initialize form states
      const settingsMap: Record<string, Record<string, string>> = {};
      const activeMap: Record<string, boolean> = {};

      items.forEach((item) => {
        settingsMap[item.provider_slug] = item.settings_json || {};
        activeMap[item.provider_slug] = item.is_active;
      });

      setFormSettings(settingsMap);
      setFormActive(activeMap);
    } catch {
      // Fail silently
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (provider: string) => {
    setSaving(provider);
    try {
      const settings = formSettings[provider] || {};
      const active = formActive[provider] ?? false;
      await apiClient.post('/integrations/', {
        provider_slug: provider,
        settings_json: settings,
        is_active: active
      });
      await fetchIntegrations();
    } catch {
      alert('Failed to save integration configuration.');
    } finally {
      setSaving(null);
    }
  };

  const handleTest = async (integrationId: string) => {
    setTesting(integrationId);
    try {
      await apiClient.post(`/integrations/test/${integrationId}`);
      alert('Verification test notification sent successfully!');
    } catch {
      alert('Verification test delivery failed.');
    } finally {
      setTesting(null);
    }
  };

  const getIntegrationConfig = (provider: string): Integration => {
    return integrations.find((i) => i.provider_slug === provider) || {
      provider_slug: provider,
      settings_json: {},
      is_active: false
    };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <RefreshCw className="h-8 w-8 text-indigo-600 animate-spin" />
      </div>
    );
  }

  const providers = [
    {
      slug: 'slack',
      name: 'Slack Notification Adapter',
      desc: 'Receive real-time naming candidates alerts in Slack channel.',
      icon: Slack,
      fields: [
        { key: 'webhook_url', label: 'Incoming Webhook URL', type: 'text', placeholder: 'https://hooks.slack.com/services/...' }
      ]
    },
    {
      slug: 'discord',
      name: 'Discord Channels Embeds',
      desc: 'Publish brand validation updates to Discord via webhook.',
      icon: MessageSquare,
      fields: [
        { key: 'webhook_url', label: 'Discord Webhook URL', type: 'text', placeholder: 'https://discord.com/api/webhooks/...' }
      ]
    },
    {
      slug: 'teams',
      name: 'Microsoft Teams Connector',
      desc: 'Deliver status reports directly to Microsoft Teams.',
      icon: Shield,
      fields: [
        { key: 'webhook_url', label: 'Office 365 Connector URL', type: 'text', placeholder: 'https://nomen.webhook.office.com/...' }
      ]
    },
    {
      slug: 'email',
      name: 'Email Automation',
      desc: 'Automate marketing reports emails to stakeholders.',
      icon: Activity,
      fields: [
        { key: 'to_email', label: 'Recipient Email Address', type: 'text', placeholder: 'stakeholder@brand.com' }
      ]
    }
  ];

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Workspace Integrations</h1>
        <p className="text-sm text-slate-500">Configure outbound channels to alert third-party systems on new brand score accomplishments.</p>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {providers.map((p) => {
          const config = getIntegrationConfig(p.slug);
          const currentSettings = formSettings[p.slug] || {};
          const currentActive = formActive[p.slug] ?? false;

          return (
            <Card key={p.slug}>
              <CardHeader className="flex flex-row items-center justify-between">
                <div className="flex items-center gap-3">
                  <p.icon className="h-8 w-8 text-indigo-600" />
                  <div>
                    <CardTitle className="text-lg font-bold">{p.name}</CardTitle>
                    <p className="text-xs text-slate-500 mt-0.5">{p.desc}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={currentActive}
                    onChange={(e) => setFormActive({ ...formActive, [p.slug]: e.target.checked })}
                    className="h-4 w-4 text-indigo-600 rounded"
                  />
                  <span className="text-xs font-semibold">{currentActive ? 'Active' : 'Inactive'}</span>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {p.fields.map((f) => (
                  <div key={f.key} className="space-y-1">
                    <label className="text-xs font-bold text-slate-500">{f.label}</label>
                    <Input
                      type={f.type}
                      placeholder={f.placeholder}
                      value={currentSettings[f.key] || ''}
                      onChange={(e) => setFormSettings({
                        ...formSettings,
                        [p.slug]: {
                          ...currentSettings,
                          [f.key]: e.target.value
                        }
                      })}
                    />
                  </div>
                ))}

                <div className="flex items-center justify-end gap-3 pt-2">
                  {config.id && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleTest(config.id!)}
                      disabled={testing === config.id}
                    >
                      {testing === config.id ? 'Sending...' : 'Test Connection'}
                    </Button>
                  )}
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => handleSave(p.slug)}
                    disabled={saving === p.slug}
                  >
                    {saving === p.slug ? 'Saving...' : 'Save Configuration'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
