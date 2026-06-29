'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as zod from 'zod';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api/client';
import { Field } from '@/components/forms/Field';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

const loginSchema = zod.object({
  email: zod.string().email('Please enter a valid email address'),
  password: zod.string().min(6, 'Password must be at least 6 characters'),
});

type LoginFields = zod.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFields>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFields) => {
    setErrorMsg(null);
    setSuccessMsg(null);
    try {
      const response = await apiClient.post('/auth/login', {
        email: data.email,
        password: data.password,
      });
      
      const userObj = response.data?.data;
      if (userObj) {
        setSuccessMsg('Login successful! Redirecting...');
        // Wait briefly for cookies state synchronization
        setTimeout(() => {
          router.push('/dashboard');
        }, 800);
      } else {
        setErrorMsg('Authentication payload format invalid.');
      }
    } catch (err: unknown) {
      const error = err as { response?: { data?: { message?: string } }; message?: string };
      setErrorMsg(error.response?.data?.message || error.message || 'Login failed.');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100">Sign In to Nomen</h2>
      
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

      <Field label="Password" error={errors.password?.message}>
        <Input
          type="password"
          placeholder="••••••••"
          error={!!errors.password}
          {...register('password')}
        />
      </Field>

      <div className="flex justify-between items-center text-xs">
        <Link href="/auth/forgot-password" className="text-indigo-600 hover:underline">
          Forgot Password?
        </Link>
        <Link href="/auth/register" className="text-indigo-600 hover:underline">
          Create account
        </Link>
      </div>

      <Button type="submit" className="w-full" isLoading={isSubmitting}>
        Sign In
      </Button>
    </form>
  );
}
