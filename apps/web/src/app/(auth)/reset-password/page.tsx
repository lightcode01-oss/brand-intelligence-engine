'use client';

import React, { useState, Suspense } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as zod from 'zod';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { apiClient } from '@/lib/api/client';
import { Field } from '@/components/forms/Field';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

const resetPasswordSchema = zod.object({
  password: zod.string().min(8, 'Password must be at least 8 characters long'),
  confirmPassword: zod.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
});

type ResetPasswordFields = zod.infer<typeof resetPasswordSchema>;

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get('token') || '';
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ResetPasswordFields>({
    resolver: zodResolver(resetPasswordSchema),
  });

  const onSubmit = async (data: ResetPasswordFields) => {
    setErrorMsg(null);
    setSuccessMsg(null);
    if (!token) {
      setErrorMsg('Required reset token is missing from the query string.');
      return;
    }
    try {
      await apiClient.post(
        `/auth/reset-password?token=${encodeURIComponent(token)}&password_new=${encodeURIComponent(data.password)}`
      );
      setSuccessMsg('Password reset completed successfully. Redirecting to sign in...');
      setTimeout(() => {
        router.push('/auth/login');
      }, 1500);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { message?: string } }; message?: string };
      setErrorMsg(error.response?.data?.message || error.message || 'Password reset resolution failed.');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100">Reset Password</h2>
      
      {errorMsg && (
        <div className="rounded-lg bg-red-50 p-3 text-xs font-medium text-red-700 dark:bg-red-950/20 dark:text-red-400">
          {errorMsg}
        </div>
      )}
      
      {successMsg && (
        <div className="rounded-lg bg-emerald-50 p-3 text-xs font-medium text-emerald-700 dark:bg-emerald-950/20 dark:text-emerald-400">
          {successMsg}
        </div>
      )}

      <Field label="New Password" error={errors.password?.message}>
        <Input
          type="password"
          placeholder="••••••••"
          error={!!errors.password}
          {...register('password')}
        />
      </Field>

      <Field label="Confirm Password" error={errors.confirmPassword?.message}>
        <Input
          type="password"
          placeholder="••••••••"
          error={!!errors.confirmPassword}
          {...register('confirmPassword')}
        />
      </Field>

      <div className="flex justify-between items-center text-xs">
        <Link href="/auth/login" className="text-indigo-600 hover:underline">
          Back to Login
        </Link>
      </div>

      <Button type="submit" className="w-full" isLoading={isSubmitting}>
        Update Password
      </Button>
    </form>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<div>Loading token validation parameters...</div>}>
      <ResetPasswordForm />
    </Suspense>
  );
}
