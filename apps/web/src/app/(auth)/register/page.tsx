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

const registerSchema = zod.object({
  email: zod.string().email('Please enter a valid email address'),
  password: zod.string().min(8, 'Password must be at least 8 characters long'),
  confirmPassword: zod.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
});

type RegisterFields = zod.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFields>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFields) => {
    setErrorMsg(null);
    setSuccessMsg(null);
    try {
      await apiClient.post('/auth/register', {
        email: data.email,
        password: data.password,
      });
      setSuccessMsg('Registration successful! Please check your email to verify.');
      setTimeout(() => {
        router.push('/auth/login');
      }, 1500);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { message?: string } }; message?: string };
      setErrorMsg(error.response?.data?.message || error.message || 'Registration failed.');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100">Create Account</h2>
      
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

      <Field label="Confirm Password" error={errors.confirmPassword?.message}>
        <Input
          type="password"
          placeholder="••••••••"
          error={!!errors.confirmPassword}
          {...register('confirmPassword')}
        />
      </Field>

      <div className="flex justify-between items-center text-xs">
        <span className="text-slate-500">Already registered?</span>
        <Link href="/auth/login" className="text-indigo-600 hover:underline">
          Sign In
        </Link>
      </div>

      <Button type="submit" className="w-full" isLoading={isSubmitting}>
        Register Account
      </Button>
    </form>
  );
}
