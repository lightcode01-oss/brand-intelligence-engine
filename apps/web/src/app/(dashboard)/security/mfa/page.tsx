'use client';

import React, { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import {
  Smartphone, ShieldCheck, ShieldAlert, QrCode, Key,
  CheckCircle, Loader2, AlertTriangle, Copy,
} from 'lucide-react';
import Link from 'next/link';

type MFAStep = 'status' | 'provision' | 'verify' | 'done';

interface MFAStatus {
  enabled: boolean;
  method: string | null;
  device_name: string | null;
  last_used_at: string | null;
}

interface ProvisionData {
  device_id: string;
  secret: string;
  otp_uri: string;
}

export default function MFASetup() {
  const [step, setStep] = useState<MFAStep>('status');
  const [status, setStatus] = useState<MFAStatus | null>(null);
  const [provision, setProvision] = useState<ProvisionData | null>(null);
  const [code, setCode] = useState('');
  const [recoveryCodes, setRecoveryCodes] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copiedSecret, setCopiedSecret] = useState(false);

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/security/mfa/status');
      setStatus(res.data?.data);
      setStep('status');
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleProvision = async () => {
    setSubmitting(true);
    setError(null);
    try {
      const res = await apiClient.post('/security/mfa/provision');
      setProvision(res.data?.data);
      setStep('provision');
    } catch {
      setError('Failed to provision MFA device. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!provision) return;
    setSubmitting(true);
    setError(null);
    try {
      const res = await apiClient.post('/security/mfa/verify', {
        device_id: provision.device_id,
        code: code.trim(),
      });
      const data = res.data?.data;
      if (data?.success) {
        setRecoveryCodes(data.recovery_codes || []);
        setStep('done');
      } else {
        setError(data?.error || 'Invalid code. Check your authenticator app and try again.');
      }
    } catch {
      setError('Verification failed. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDisable = async () => {
    if (!confirm('Are you sure you want to disable MFA? Your account will be less secure.')) return;
    setSubmitting(true);
    try {
      await apiClient.delete('/security/mfa/disable');
      await fetchStatus();
    } finally {
      setSubmitting(false);
    }
  };

  const copySecret = () => {
    if (provision?.secret) {
      navigator.clipboard.writeText(provision.secret);
      setCopiedSecret(true);
      setTimeout(() => setCopiedSecret(false), 2000);
    }
  };

  const SecurityNavTabs = () => (
    <div className="flex gap-1 border-b border-slate-200 dark:border-slate-800 pb-px text-sm">
      {[
        { label: 'Overview', href: '/security' },
        { label: 'MFA', href: '/security/mfa', active: true },
        { label: 'Sessions', href: '/security/sessions' },
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

  if (loading) {
    return (
      <div className="flex justify-center items-center py-32">
        <Loader2 className="h-12 w-12 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <Smartphone className="h-6 w-6 text-indigo-600" />
          Two-Factor Authentication
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Secure your account with a TOTP authenticator app like Google Authenticator or Authy.
        </p>
      </div>

      <SecurityNavTabs />

      {/* STATUS VIEW */}
      {step === 'status' && status && (
        <Card>
          <CardContent className="pt-6 space-y-6">
            <div className="flex items-center justify-between p-4 rounded-xl border border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-3">
                {status.enabled
                  ? <ShieldCheck className="h-8 w-8 text-emerald-600" />
                  : <ShieldAlert className="h-8 w-8 text-red-500" />}
                <div>
                  <p className="font-semibold text-slate-900 dark:text-white">
                    MFA is {status.enabled ? 'Enabled' : 'Disabled'}
                  </p>
                  {status.enabled && status.last_used_at && (
                    <p className="text-xs text-slate-500 mt-0.5">
                      Last used: {new Date(status.last_used_at).toLocaleString()}
                    </p>
                  )}
                </div>
              </div>
              {status.enabled ? (
                <Button variant="outline" size="sm" onClick={handleDisable} disabled={submitting}
                  className="text-red-600 border-red-200 hover:bg-red-50">
                  Disable MFA
                </Button>
              ) : (
                <Button size="sm" onClick={handleProvision} disabled={submitting}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white">
                  {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Enable MFA'}
                </Button>
              )}
            </div>

            {!status.enabled && (
              <div className="rounded-xl bg-amber-50 dark:bg-amber-950/10 border border-amber-200 dark:border-amber-900/20 p-4 text-sm text-amber-700 dark:text-amber-400 flex gap-3">
                <AlertTriangle className="h-5 w-5 shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold">Your account is not protected by MFA.</p>
                  <p className="mt-1">Enable two-factor authentication to significantly reduce the risk of unauthorized access.</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* PROVISION VIEW — QR Code + Secret */}
      {step === 'provision' && provision && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base font-semibold flex items-center gap-2">
              <QrCode className="h-5 w-5 text-indigo-600" />
              Scan QR Code in Your Authenticator App
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-5">
            {/* QR Code display via external QR service */}
            <div className="flex justify-center">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(provision.otp_uri)}`}
                alt="MFA QR Code"
                className="w-48 h-48 rounded-xl border border-slate-200 dark:border-slate-700 p-2"
              />
            </div>

            <p className="text-xs text-slate-500 text-center">
              Cannot scan? Enter the secret key manually:
            </p>
            <div className="flex items-center gap-2 p-3 rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
              <code className="text-xs font-mono text-slate-700 dark:text-slate-300 break-all flex-1">
                {provision.secret}
              </code>
              <button onClick={copySecret} className="p-1.5 rounded hover:bg-slate-200 dark:hover:bg-slate-700 transition">
                <Copy className="h-3.5 w-3.5 text-slate-500" />
              </button>
            </div>
            {copiedSecret && <p className="text-xs text-emerald-600 text-center">Copied to clipboard!</p>}

            <Button size="sm" onClick={() => setStep('verify')} className="w-full bg-indigo-600 hover:bg-indigo-700 text-white">
              I Have Scanned the QR Code →
            </Button>
          </CardContent>
        </Card>
      )}

      {/* VERIFY VIEW — Enter code */}
      {step === 'verify' && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base font-semibold flex items-center gap-2">
              <Key className="h-5 w-5 text-indigo-600" />
              Enter Verification Code
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleVerify} className="space-y-4">
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Enter the 6-digit code from your authenticator app to complete setup.
              </p>
              <Input
                placeholder="000000"
                value={code}
                onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                maxLength={6}
                className="text-center text-2xl font-mono tracking-[0.5em] h-14"
                autoFocus
              />
              {error && (
                <p className="text-sm text-red-500 flex items-center gap-1">
                  <AlertTriangle className="h-4 w-4" /> {error}
                </p>
              )}
              <Button type="submit" disabled={submitting || code.length !== 6} className="w-full bg-indigo-600 hover:bg-indigo-700 text-white">
                {submitting ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                Verify & Activate MFA
              </Button>
              <button type="button" onClick={() => setStep('provision')} className="text-xs text-slate-400 hover:text-slate-600 w-full text-center">
                ← Back to QR Code
              </button>
            </form>
          </CardContent>
        </Card>
      )}

      {/* DONE VIEW — Recovery Codes */}
      {step === 'done' && (
        <Card className="border-emerald-200 dark:border-emerald-900/20">
          <CardContent className="pt-6 space-y-5">
            <div className="flex items-center gap-3">
              <CheckCircle className="h-8 w-8 text-emerald-600" />
              <div>
                <p className="font-bold text-slate-900 dark:text-white">MFA Successfully Enabled!</p>
                <p className="text-sm text-slate-500">Save your recovery codes in a secure location.</p>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-900 dark:bg-slate-800 border border-slate-700">
              <p className="text-xs font-semibold text-slate-400 uppercase mb-3">Recovery Codes (save these now)</p>
              <div className="grid grid-cols-2 gap-2">
                {recoveryCodes.map((rc) => (
                  <code key={rc} className="text-xs font-mono text-emerald-400 bg-slate-800 dark:bg-slate-700 px-2 py-1 rounded">
                    {rc}
                  </code>
                ))}
              </div>
            </div>

            <div className="rounded-lg bg-amber-50 dark:bg-amber-950/10 border border-amber-200 p-3 text-xs text-amber-700 dark:text-amber-400">
              ⚠️ These codes can only be viewed once. Store them in a password manager or secure vault.
            </div>

            <Button onClick={fetchStatus} className="w-full bg-indigo-600 hover:bg-indigo-700 text-white">
              Done
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
