'use client';

import React, { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
  Monitor, Smartphone, Trash2, LogOut,
  Loader2, AlertTriangle, CheckCircle,
} from 'lucide-react';
import Link from 'next/link';

interface Session {
  id: string;
  device_name: string | null;
  browser: string | null;
  os: string | null;
  ip_address: string | null;
  country: string | null;
  last_seen_at: string;
  expires_at: string;
  created_at: string;
}

export default function SessionManager() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [revoking, setRevoking] = useState<string | null>(null);
  const [revokingAll, setRevokingAll] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const fetchSessions = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/security/sessions');
      setSessions(res.data?.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  const handleRevoke = async (id: string) => {
    setRevoking(id);
    try {
      await apiClient.delete(`/security/sessions/${id}`);
      setSessions((prev) => prev.filter((s) => s.id !== id));
      showSuccess('Session revoked successfully.');
    } catch (err) {
      console.error(err);
    } finally {
      setRevoking(null);
    }
  };

  const handleRevokeAll = async () => {
    if (!confirm('Sign out from all devices? This will end all your active sessions.')) return;
    setRevokingAll(true);
    try {
      await apiClient.delete('/security/sessions');
      setSessions([]);
      showSuccess('All sessions revoked. You have been signed out everywhere.');
    } catch (err) {
      console.error(err);
    } finally {
      setRevokingAll(false);
    }
  };

  const showSuccess = (msg: string) => {
    setSuccessMsg(msg);
    setTimeout(() => setSuccessMsg(null), 4000);
  };

  const getDeviceIcon = (os: string | null) => {
    if (!os) return Monitor;
    const lower = os.toLowerCase();
    if (lower.includes('ios') || lower.includes('android')) return Smartphone;
    return Monitor;
  };

  const SecurityNavTabs = () => (
    <div className="flex gap-1 border-b border-slate-200 dark:border-slate-800 pb-px text-sm">
      {[
        { label: 'Overview', href: '/security' },
        { label: 'MFA', href: '/security/mfa' },
        { label: 'Sessions', href: '/security/sessions', active: true },
        { label: 'Audit Log', href: '/security/audit' },
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
    <div className="space-y-6 max-w-3xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Monitor className="h-6 w-6 text-indigo-600" />
            Active Sessions
          </h1>
          <p className="text-sm text-slate-500 mt-1">Manage all your currently active device sessions.</p>
        </div>
        {sessions.length > 1 && (
          <Button
            variant="outline"
            size="sm"
            onClick={handleRevokeAll}
            disabled={revokingAll}
            className="text-red-600 border-red-200 hover:bg-red-50 flex items-center gap-1"
          >
            {revokingAll ? <Loader2 className="h-4 w-4 animate-spin" /> : <LogOut className="h-4 w-4" />}
            Sign Out All
          </Button>
        )}
      </div>

      <SecurityNavTabs />

      {successMsg && (
        <div className="flex items-center gap-2 p-3 rounded-lg bg-emerald-50 dark:bg-emerald-950/10 border border-emerald-200 text-emerald-700 text-sm">
          <CheckCircle className="h-4 w-4 shrink-0" />
          {successMsg}
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center py-20">
          <Loader2 className="h-10 w-10 animate-spin text-indigo-600" />
        </div>
      ) : sessions.length === 0 ? (
        <Card>
          <CardContent className="pt-6 text-center py-12">
            <Monitor className="h-12 w-12 text-slate-300 mx-auto mb-3" />
            <p className="text-slate-500 text-sm">No active sessions found.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {sessions.map((session, idx) => {
            const DeviceIcon = getDeviceIcon(session.os);
            const isCurrentApprox = idx === 0;
            return (
              <Card key={session.id} className={isCurrentApprox ? 'border-indigo-200 dark:border-indigo-800' : ''}>
                <CardContent className="pt-4 pb-4 flex items-center justify-between gap-4">
                  <div className="flex items-center gap-4">
                    <div className={`p-2.5 rounded-xl ${isCurrentApprox ? 'bg-indigo-50 text-indigo-600' : 'bg-slate-100 dark:bg-slate-800 text-slate-500'}`}>
                      <DeviceIcon className="h-5 w-5" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-semibold text-slate-900 dark:text-white">
                          {session.device_name || `${session.browser} on ${session.os}`}
                        </p>
                        {isCurrentApprox && (
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-600 font-bold">
                            Current
                          </span>
                        )}
                      </div>
                      <div className="flex gap-3 mt-0.5 text-xs text-slate-400">
                        {session.ip_address && <span>{session.ip_address}</span>}
                        {session.country && <span>{session.country}</span>}
                        <span>Last seen: {new Date(session.last_seen_at).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                  {!isCurrentApprox && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleRevoke(session.id)}
                      disabled={revoking === session.id}
                      className="text-red-600 border-red-200 hover:bg-red-50 shrink-0"
                    >
                      {revoking === session.id ? (
                        <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      ) : (
                        <Trash2 className="h-3.5 w-3.5" />
                      )}
                    </Button>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      <Card className="bg-amber-50/50 dark:bg-amber-950/10 border-amber-100 dark:border-amber-900/20">
        <CardContent className="pt-4 pb-4 flex items-start gap-3 text-sm text-amber-700 dark:text-amber-400">
          <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" />
          <p>
            If you see an unrecognized session, revoke it immediately and change your password.
            Enable MFA for additional protection.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
