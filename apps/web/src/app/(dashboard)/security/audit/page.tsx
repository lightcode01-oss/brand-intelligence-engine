'use client';

import React, { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { Card, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import {
  FileText, Search, Shield, Loader2,
} from 'lucide-react';
import Link from 'next/link';

interface AuditEvent {
  id: string;
  event_type: string;
  actor: string;
  ip_address: string | null;
  risk_score: number;
  metadata: Record<string, unknown>;
  created_at: string;
}

const RISK_COLOR: Record<string, string> = {
  high: 'text-red-600 bg-red-50 dark:bg-red-950/20 border-red-200',
  medium: 'text-amber-600 bg-amber-50 dark:bg-amber-950/20 border-amber-200',
  low: 'text-emerald-600 bg-emerald-50 dark:bg-emerald-950/20 border-emerald-200',
};

const EVENT_TYPE_COLOR: Record<string, string> = {
  LOGIN_FAILED: 'text-red-600',
  ACCOUNT_LOCKED: 'text-red-700 font-bold',
  DATA_DELETION_REQUESTED: 'text-red-700 font-bold',
  MFA_DISABLED: 'text-amber-600',
  ROLE_CHANGED: 'text-amber-600',
  PASSWORD_CHANGED: 'text-amber-600',
  LOGIN_SUCCESS: 'text-emerald-600',
  MFA_ENABLED: 'text-emerald-600',
  SESSION_REVOKED: 'text-slate-600',
};

export default function AuditLogViewer() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchType, setSearchType] = useState('');
  const [sinceHours, setSinceHours] = useState(72);

  const fetchAudit = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ since_hours: sinceHours.toString(), limit: '200' });
      if (searchType) params.set('event_type', searchType.toUpperCase());
      const res = await apiClient.get(`/security/audit?${params.toString()}`);
      setEvents(res.data?.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAudit();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sinceHours]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchAudit();
  };

  const getRiskLevel = (score: number) => {
    if (score >= 60) return 'high';
    if (score >= 30) return 'medium';
    return 'low';
  };

  const SecurityNavTabs = () => (
    <div className="flex gap-1 border-b border-slate-200 dark:border-slate-800 pb-px text-sm">
      {[
        { label: 'Overview', href: '/security' },
        { label: 'MFA', href: '/security/mfa' },
        { label: 'Sessions', href: '/security/sessions' },
        { label: 'Audit Log', href: '/security/audit', active: true },
        { label: 'SSO', href: '/security/sso' },
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
    <div className="space-y-6 max-w-5xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <FileText className="h-6 w-6 text-indigo-600" />
            Security Audit Log
          </h1>
          <p className="text-sm text-slate-500 mt-1">Immutable record of all security-relevant events.</p>
        </div>
        {/* Time range selector */}
        <select
          value={sinceHours}
          onChange={(e) => setSinceHours(Number(e.target.value))}
          className="text-sm px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300"
        >
          <option value={24}>Last 24h</option>
          <option value={72}>Last 72h</option>
          <option value={168}>Last 7 days</option>
          <option value={720}>Last 30 days</option>
        </select>
      </div>

      <SecurityNavTabs />

      {/* Search bar */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <Input
          placeholder="Filter by event type (e.g. LOGIN_FAILED)..."
          value={searchType}
          onChange={(e) => setSearchType(e.target.value)}
          className="flex-1 h-9 text-sm uppercase"
        />
        <Button type="submit" size="sm" className="bg-indigo-600 hover:bg-indigo-700 text-white h-9">
          <Search className="h-4 w-4" />
        </Button>
      </form>

      {/* Summary chips */}
      {!loading && events.length > 0 && (
        <div className="flex gap-3 flex-wrap text-xs">
          <span className="px-3 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 font-semibold">
            {events.length} events
          </span>
          <span className="px-3 py-1 rounded-full bg-red-50 dark:bg-red-950/20 text-red-600 font-semibold border border-red-100">
            {events.filter((e) => e.risk_score >= 60).length} high-risk
          </span>
          <span className="px-3 py-1 rounded-full bg-amber-50 dark:bg-amber-950/20 text-amber-600 font-semibold border border-amber-100">
            {events.filter((e) => e.risk_score >= 30 && e.risk_score < 60).length} medium-risk
          </span>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center py-20">
          <Loader2 className="h-10 w-10 animate-spin text-indigo-600" />
        </div>
      ) : events.length === 0 ? (
        <Card>
          <CardContent className="pt-6 py-12 text-center">
            <Shield className="h-12 w-12 text-slate-300 mx-auto mb-3" />
            <p className="text-slate-500 text-sm">No security events found for the selected period.</p>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-0 overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/10 text-slate-500 uppercase font-semibold">
                  <th className="p-3">Timestamp</th>
                  <th className="p-3">Event Type</th>
                  <th className="p-3">Actor</th>
                  <th className="p-3">IP Address</th>
                  <th className="p-3">Risk</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {events.map((event) => {
                  const riskLevel = getRiskLevel(event.risk_score);
                  return (
                    <tr key={event.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-900/5">
                      <td className="p-3 whitespace-nowrap text-slate-500">
                        {new Date(event.created_at).toLocaleString()}
                      </td>
                      <td className={`p-3 font-semibold ${EVENT_TYPE_COLOR[event.event_type] || 'text-slate-700 dark:text-slate-300'}`}>
                        {event.event_type}
                      </td>
                      <td className="p-3 text-slate-600 dark:text-slate-400">{event.actor}</td>
                      <td className="p-3 text-slate-500">{event.ip_address || '—'}</td>
                      <td className="p-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${RISK_COLOR[riskLevel]}`}>
                          {riskLevel.toUpperCase()} {event.risk_score}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
