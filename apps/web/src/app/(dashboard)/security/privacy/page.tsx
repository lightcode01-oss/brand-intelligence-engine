'use client';

import React, { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
  Lock, Download, Trash2, CheckCircle, AlertTriangle, Loader2, ToggleLeft, ToggleRight,
} from 'lucide-react';
import Link from 'next/link';

interface ConsentState {
  marketing: boolean;
  analytics: boolean;
  necessary: boolean;
}

interface DeletionStatus {
  has_request: boolean;
  status?: string;
  scheduled_for?: string;
}

export default function PrivacyControls() {
  const [exportLoading, setExportLoading] = useState(false);
  const [exportResult, setExportResult] = useState<{ download_url?: string } | null>(null);
  const [deletionStatus, setDeletionStatus] = useState<DeletionStatus | null>(null);
  const [deletionLoading, setDeletionLoading] = useState(false);
  const [cancelling, setCancelling] = useState(false);
  const [loading, setLoading] = useState(true);
  const [consent, setConsent] = useState<ConsentState>({ marketing: false, analytics: true, necessary: true });
  const [savingConsent, setSavingConsent] = useState(false);
  const [consentSaved, setConsentSaved] = useState(false);

  useEffect(() => {
    const fetchStatus = async () => {
      setLoading(true);
      try {
        const res = await apiClient.get('/security/gdpr/delete/status');
        setDeletionStatus(res.data?.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchStatus();
  }, []);

  const handleRequestExport = async () => {
    setExportLoading(true);
    try {
      const res = await apiClient.post('/security/gdpr/export');
      setExportResult(res.data?.data);
    } catch (err) {
      console.error(err);
    } finally {
      setExportLoading(false);
    }
  };

  const handleRequestDeletion = async () => {
    if (!confirm('This will permanently schedule your account for deletion in 30 days. Are you sure?')) return;
    setDeletionLoading(true);
    try {
      const res = await apiClient.post('/security/gdpr/delete', { reason: 'User requested deletion' });
      setDeletionStatus({ has_request: true, ...res.data?.data });
    } catch (err) {
      console.error(err);
    } finally {
      setDeletionLoading(false);
    }
  };

  const handleCancelDeletion = async () => {
    setCancelling(true);
    try {
      await apiClient.delete('/security/gdpr/delete/cancel');
      setDeletionStatus({ has_request: false });
    } catch (err) {
      console.error(err);
    } finally {
      setCancelling(false);
    }
  };

  const handleSaveConsent = async () => {
    setSavingConsent(true);
    try {
      for (const [type, granted] of Object.entries(consent)) {
        if (type === 'necessary') continue;
        await apiClient.post('/security/gdpr/consent', { consent_type: type, granted });
      }
      setConsentSaved(true);
      setTimeout(() => setConsentSaved(false), 3000);
    } catch (err) {
      console.error(err);
    } finally {
      setSavingConsent(false);
    }
  };

  const SecurityNavTabs = () => (
    <div className="flex gap-1 border-b border-slate-200 dark:border-slate-800 pb-px text-sm">
      {[
        { label: 'Overview', href: '/security' },
        { label: 'MFA', href: '/security/mfa' },
        { label: 'Sessions', href: '/security/sessions' },
        { label: 'Audit Log', href: '/security/audit' },
        { label: 'SSO', href: '/security/sso' },
        { label: 'Privacy', href: '/security/privacy', active: true },
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

  const ConsentToggle = ({ label, key, value, fixed }: { label: string; key: keyof ConsentState; value: boolean; fixed?: boolean }) => (
    <div className="flex items-center justify-between py-3 border-b border-slate-100 dark:border-slate-800 last:border-0">
      <div>
        <p className="text-sm font-semibold text-slate-900 dark:text-white capitalize">{label} {fixed && <span className="text-[10px] text-slate-400 ml-1">(Required)</span>}</p>
      </div>
      <button
        onClick={() => !fixed && setConsent(prev => ({ ...prev, [key]: !prev[key] }))}
        disabled={fixed}
        className={`transition ${fixed ? 'opacity-50 cursor-not-allowed' : 'hover:opacity-80'}`}
      >
        {value
          ? <ToggleRight className="h-7 w-7 text-indigo-600" />
          : <ToggleLeft className="h-7 w-7 text-slate-400" />}
      </button>
    </div>
  );

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <Lock className="h-6 w-6 text-indigo-600" />
          Privacy & GDPR Controls
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Manage your consent preferences, request data exports, or delete your account.
        </p>
      </div>

      <SecurityNavTabs />

      {loading ? (
        <div className="flex justify-center items-center py-20">
          <Loader2 className="h-10 w-10 animate-spin text-indigo-600" />
        </div>
      ) : (
        <div className="space-y-6">
          {/* Consent preferences */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-semibold">Cookie & Data Consent Preferences</CardTitle>
            </CardHeader>
            <CardContent className="space-y-0">
              <ConsentToggle label="Necessary" key="necessary" value={consent.necessary} fixed />
              <ConsentToggle label="Analytics" key="analytics" value={consent.analytics} />
              <ConsentToggle label="Marketing" key="marketing" value={consent.marketing} />
              <div className="pt-4 flex items-center gap-3">
                <Button onClick={handleSaveConsent} disabled={savingConsent} size="sm" className="bg-indigo-600 hover:bg-indigo-700 text-white">
                  {savingConsent ? <Loader2 className="h-3.5 w-3.5 animate-spin mr-1" /> : null}
                  Save Preferences
                </Button>
                {consentSaved && (
                  <span className="text-xs text-emerald-600 flex items-center gap-1">
                    <CheckCircle className="h-3.5 w-3.5" /> Saved
                  </span>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Data Export */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-semibold flex items-center gap-2">
                <Download className="h-4 w-4 text-indigo-600" />
                Request Data Export (GDPR Art. 20)
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Download a complete export of all your personal data, workspace activity, and account information.
              </p>
              <Button
                onClick={handleRequestExport}
                disabled={exportLoading}
                size="sm"
                variant="outline"
                className="flex items-center gap-2"
              >
                {exportLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
                Generate Data Export
              </Button>
              {exportResult?.download_url && (
                <div className="mt-3 p-3 rounded-lg bg-emerald-50 dark:bg-emerald-950/10 border border-emerald-200 text-sm text-emerald-700 dark:text-emerald-400 flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 shrink-0" />
                  Export ready.{' '}
                  <a href={exportResult.download_url} className="underline font-semibold">
                    Download your data
                  </a>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Account Deletion */}
          <Card className="border-red-100 dark:border-red-950/20">
            <CardHeader>
              <CardTitle className="text-sm font-semibold text-red-600 flex items-center gap-2">
                <Trash2 className="h-4 w-4" />
                Request Account Deletion (GDPR Art. 17)
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {deletionStatus?.has_request ? (
                <div className="space-y-3">
                  <div className="p-3 rounded-lg bg-red-50 dark:bg-red-950/10 border border-red-200 text-sm text-red-700 dark:text-red-400">
                    <p className="font-semibold flex items-center gap-1">
                      <AlertTriangle className="h-4 w-4" /> Deletion Pending
                    </p>
                    <p className="mt-1">
                      Your account is scheduled for deletion on{' '}
                      <strong>{deletionStatus.scheduled_for ? new Date(deletionStatus.scheduled_for).toLocaleDateString() : 'N/A'}</strong>.
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleCancelDeletion}
                    disabled={cancelling}
                    className="text-slate-700"
                  >
                    {cancelling ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : null}
                    Cancel Deletion Request
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  <p className="text-sm text-slate-600 dark:text-slate-400">
                    Permanently delete your account and all associated data after a 30-day grace period.
                    This action cannot be undone after the grace period expires.
                  </p>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleRequestDeletion}
                    disabled={deletionLoading}
                    className="text-red-600 border-red-200 hover:bg-red-50"
                  >
                    {deletionLoading ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : <Trash2 className="h-4 w-4 mr-1" />}
                    Request Account Deletion
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
