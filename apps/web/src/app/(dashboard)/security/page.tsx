'use client';

import React, { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
  ShieldCheck, ShieldAlert, Smartphone, Monitor, Globe,
  FileText, Lock, UserCheck, AlertTriangle,
  Loader2, RefreshCw, ChevronRight,
} from 'lucide-react';
import Link from 'next/link';

interface SecurityOverview {
  mfa_enabled: boolean;
  active_sessions: number;
  recent_events: number;
  high_risk_events: number;
  pending_export: boolean;
  pending_deletion: boolean;
}

export default function SecurityCenter() {
  const [loading, setLoading] = useState(true);
  const [overview, setOverview] = useState<SecurityOverview | null>(null);

  useEffect(() => {
    const fetchOverview = async () => {
      try {
        const [mfaRes, sessionsRes, auditRes] = await Promise.allSettled([
          apiClient.get('/security/mfa/status'),
          apiClient.get('/security/sessions'),
          apiClient.get('/security/audit?since_hours=24&limit=50'),
        ]);
        const mfaData = mfaRes.status === 'fulfilled' ? mfaRes.value.data?.data : null;
        const sessionsData = sessionsRes.status === 'fulfilled' ? sessionsRes.value.data?.data : [];
        const auditData = auditRes.status === 'fulfilled' ? auditRes.value.data?.data : [];

        const highRisk = Array.isArray(auditData)
          ? auditData.filter((e: { risk_score: number }) => e.risk_score >= 40).length
          : 0;

        setOverview({
          mfa_enabled: mfaData?.enabled ?? false,
          active_sessions: Array.isArray(sessionsData) ? sessionsData.length : 0,
          recent_events: Array.isArray(auditData) ? auditData.length : 0,
          high_risk_events: highRisk,
          pending_export: false,
          pending_deletion: false,
        });
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchOverview();
  }, []);

  const securityScore = overview
    ? Math.round(
        (overview.mfa_enabled ? 40 : 0) +
        (overview.high_risk_events === 0 ? 40 : Math.max(0, 40 - overview.high_risk_events * 5)) +
        20
      )
    : 0;

  const cards = [
    {
      title: 'Two-Factor Authentication',
      description: 'Protect your account with TOTP MFA.',
      icon: Smartphone,
      status: overview?.mfa_enabled ? 'Enabled' : 'Disabled',
      statusColor: overview?.mfa_enabled ? 'text-emerald-600' : 'text-red-500',
      href: '/security/mfa',
    },
    {
      title: 'Active Sessions',
      description: 'Review and revoke device sessions.',
      icon: Monitor,
      status: `${overview?.active_sessions ?? 0} session(s)`,
      statusColor: 'text-indigo-600',
      href: '/security/sessions',
    },
    {
      title: 'Audit Log',
      description: 'Immutable record of all security events.',
      icon: FileText,
      status: `${overview?.recent_events ?? 0} event(s) today`,
      statusColor: 'text-slate-600',
      href: '/security/audit',
    },
    {
      title: 'SSO Configuration',
      description: 'Connect Google, Microsoft, or Okta.',
      icon: Globe,
      status: 'Configure',
      statusColor: 'text-blue-600',
      href: '/security/sso',
    },
    {
      title: 'Privacy & GDPR',
      description: 'Manage consent, exports, and deletion.',
      icon: Lock,
      status: 'Manage',
      statusColor: 'text-purple-600',
      href: '/security/privacy',
    },
  ];

  return (
    <div className="space-y-6 max-w-6xl">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <ShieldCheck className="h-7 w-7 text-indigo-600" />
            Security Center
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Manage authentication, sessions, audit logs, SSO, and privacy controls.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={() => window.location.reload()} className="flex items-center gap-1">
          <RefreshCw className="h-4 w-4" />
          Refresh
        </Button>
      </div>

      {/* Navigation tabs */}
      <div className="flex gap-1 border-b border-slate-200 dark:border-slate-800 pb-px text-sm">
        {[
          { label: 'Overview', href: '/security' },
          { label: 'MFA', href: '/security/mfa' },
          { label: 'Sessions', href: '/security/sessions' },
          { label: 'Audit Log', href: '/security/audit' },
          { label: 'SSO', href: '/security/sso' },
          { label: 'Privacy', href: '/security/privacy' },
        ].map((tab) => (
          <Link
            key={tab.href}
            href={tab.href}
            className={`px-4 py-2 font-medium transition ${
              tab.href === '/security'
                ? 'border-b-2 border-indigo-600 text-indigo-600'
                : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
            }`}
          >
            {tab.label}
          </Link>
        ))}
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-32">
          <Loader2 className="h-12 w-12 animate-spin text-indigo-600" />
        </div>
      ) : (
        <div className="space-y-6">
          {/* Security Score Card */}
          <Card className="border-indigo-100 dark:border-indigo-950/20 bg-gradient-to-br from-indigo-50 to-white dark:from-indigo-950/10 dark:to-slate-900">
            <CardContent className="pt-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div>
                <p className="text-xs uppercase font-semibold text-indigo-600 tracking-wider">Security Score</p>
                <p className="text-5xl font-extrabold text-slate-900 dark:text-white mt-1">{securityScore}<span className="text-xl text-slate-400">/100</span></p>
                <p className="text-sm text-slate-500 mt-2">
                  {securityScore >= 80 ? '🟢 Strong security posture' : securityScore >= 50 ? '🟡 Moderate — enable MFA to improve' : '🔴 Weak — enable MFA immediately'}
                </p>
              </div>
              <div className="flex flex-col gap-2 text-sm">
                <div className="flex items-center gap-2">
                  {overview?.mfa_enabled
                    ? <ShieldCheck className="h-4 w-4 text-emerald-600" />
                    : <ShieldAlert className="h-4 w-4 text-red-500" />}
                  <span className={overview?.mfa_enabled ? 'text-emerald-600 font-semibold' : 'text-red-500'}>
                    MFA {overview?.mfa_enabled ? 'Active' : 'Not Set Up'}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <UserCheck className="h-4 w-4 text-indigo-600" />
                  <span className="text-slate-600 dark:text-slate-400">{overview?.active_sessions} active session(s)</span>
                </div>
                {overview && overview.high_risk_events > 0 && (
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-amber-500" />
                    <span className="text-amber-600 font-semibold">{overview.high_risk_events} high-risk event(s) in 24h</span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Feature cards */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {cards.map((card) => (
              <Link key={card.href} href={card.href}>
                <Card className="hover:shadow-md hover:border-indigo-200 dark:hover:border-indigo-800 transition cursor-pointer h-full">
                  <CardContent className="pt-6 flex flex-col h-full">
                    <div className="flex items-start justify-between mb-3">
                      <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-950/20">
                        <card.icon className="h-5 w-5 text-indigo-600" />
                      </div>
                      <ChevronRight className="h-4 w-4 text-slate-400" />
                    </div>
                    <p className="font-semibold text-slate-900 dark:text-white text-sm">{card.title}</p>
                    <p className="text-xs text-slate-500 mt-1 flex-1">{card.description}</p>
                    <p className={`text-xs font-bold mt-3 ${card.statusColor}`}>{card.status}</p>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
