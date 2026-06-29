'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { apiClient } from '@/lib/api/client';
import { Button } from '@/components/ui/Button';

function VerifyEmailForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get('token') || '';
  const [statusState, setStatusState] = useState<'verifying' | 'success' | 'error'>('verifying');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      setStatusState('error');
      setErrorMsg('Verification token is missing from parameters.');
      return;
    }

    const triggerVerification = async () => {
      try {
        await apiClient.post(`/auth/verify-email?token=${encodeURIComponent(token)}`);
        setStatusState('success');
        setTimeout(() => {
          router.push('/auth/login');
        }, 2000);
      } catch (err: unknown) {
        const error = err as { response?: { data?: { message?: string } }; message?: string };
        setStatusState('error');
        setErrorMsg(error.response?.data?.message || error.message || 'Verification failed.');
      }
    };

    triggerVerification();
  }, [token, router]);

  return (
    <div className="text-center space-y-4">
      <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100">Email Verification</h2>
      
      {statusState === 'verifying' && (
        <div className="space-y-2">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-indigo-600" />
          <p className="text-xs text-slate-500">Verifying your signature token...</p>
        </div>
      )}

      {statusState === 'success' && (
        <div className="rounded-lg bg-emerald-50 p-4 text-xs font-medium text-emerald-700 dark:bg-emerald-950/20 dark:text-emerald-400">
          ✓ Email verified successfully! Redirecting to login...
        </div>
      )}

      {statusState === 'error' && (
        <div className="space-y-4">
          <div className="rounded-lg bg-red-50 p-4 text-xs font-medium text-red-700 dark:bg-red-950/20 dark:text-red-400">
            {errorMsg || 'Failed to verify email.'}
          </div>
          <Link href="/auth/login" className="inline-block">
            <Button variant="outline" size="sm">Back to Login</Button>
          </Link>
        </div>
      )}
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<div>Loading verification tokens...</div>}>
      <VerifyEmailForm />
    </Suspense>
  );
}
