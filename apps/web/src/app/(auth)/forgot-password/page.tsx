'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as zod from 'zod';
import Link from 'next/link';
import { apiClient } from '@/lib/api/client';
import { Field } from '@/components/forms/Field';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

const forgotPasswordSchema = zod.object({
  email: zod.string().email('Please enter a valid email address'),
});

type ForgotPasswordFields = zod.infer<typeof forgotPasswordSchema>;

export default function ForgotPasswordPage() {
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ForgotPasswordFields>({
    resolver: zodResolver(forgotPasswordSchema),
  });

  const onSubmit = async (data: ForgotPasswordFields) => {
    setErrorMsg(null);
    setSuccessMsg(null);
    try {
      await apiClient.post(`/auth/forgot-password?email=${encodeURIComponent(data.email)}`);
      setSuccessMsg('Reset instruction email sent. Please check your inbox.');
    } catch (err: unknown) {
      const error = err as { response?: { data?: { message?: string } }; message?: string };
      setErrorMsg(error.response?.data?.message || error.message || 'Verification email submission failed.');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100">Forgot Password</h2>
      <p className="text-xs text-slate-500">Provide your email address to receive password reset instructions.</p>
      
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

      <Field label="Email Address" error={errors.email?.message}>
        <Input
          type="email"
          placeholder="developer@nomen.ai"
          error={!!errors.email}
          {...register('email')}
        />
      </Field>

      <div className="flex justify-between items-center text-xs">
        <Link href="/auth/login" className="text-indigo-600 hover:underline">
          Back to Login
        </Link>
      </div>

      <Button type="submit" className="w-full" isLoading={isSubmitting}>
        Send Reset Email
      </Button>
    </form>
  );
}
