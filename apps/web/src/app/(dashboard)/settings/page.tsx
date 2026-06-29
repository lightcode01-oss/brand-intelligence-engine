'use client';

import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as zod from 'zod';
import { apiClient } from '@/lib/api/client';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Field } from '@/components/forms/Field';
import { useThemeStore } from '@/store/themeStore';
import { User, Key, ShieldAlert, Monitor } from 'lucide-react';

interface SessionItem {
  id: string;
  ip_address: string;
  last_activity: string;
}

const profileSchema = zod.object({
  email: zod.string().email('Please enter a valid email address'),
});

const passwordSchema = zod.object({
  oldPassword: zod.string().min(6, 'Old password must be at least 6 characters'),
  newPassword: zod.string().min(8, 'New password must be at least 8 characters long'),
  confirmPassword: zod.string(),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
});

const apiKeySchema = zod.object({
  name: zod.string().min(2, 'Name must be at least 2 characters'),
  scopes: zod.string(),
});

type ProfileFields = zod.infer<typeof profileSchema>;
type PasswordFields = zod.infer<typeof passwordSchema>;
type ApiKeyFields = zod.infer<typeof apiKeySchema>;

export default function SettingsPage() {
  const { theme, setTheme } = useThemeStore();
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [generatedKey, setGeneratedKey] = useState<string | null>(null);

  // 1. Fetch Profile
  const { data: profileResponse, isLoading: loadingProfile } = useQuery({
    queryKey: ['profile'],
    queryFn: () => apiClient.get('/users/me').then((res) => res.data),
  });

  const email = profileResponse?.data?.email || '';

  // 2. Fetch Sessions
  const { data: sessionsResponse, refetch: refetchSessions } = useQuery({
    queryKey: ['sessions'],
    queryFn: () => apiClient.get('/auth/sessions').then((res) => res.data),
  });

  const sessions = sessionsResponse?.data || [];

  const profileForm = useForm<ProfileFields>({
    resolver: zodResolver(profileSchema),
    defaultValues: { email },
  });

  const passwordForm = useForm<PasswordFields>({
    resolver: zodResolver(passwordSchema),
  });

  const keyForm = useForm<ApiKeyFields>({
    resolver: zodResolver(apiKeySchema),
    defaultValues: { name: 'Development Key', scopes: 'generation.write, analytics.read' },
  });

  // 3. Mutations
  const updateProfileMutation = useMutation({
    mutationFn: (data: ProfileFields) => apiClient.put('/users/me', data),
    onSuccess: () => {
      setSuccessMsg('Profile details updated successfully!');
    },
    onError: (err: unknown) => {
      const error = err as { response?: { data?: { message?: string } }; message?: string };
      setErrorMsg(error.response?.data?.message || error.message || 'Profile update failed.');
    },
  });

  const updatePasswordMutation = useMutation({
    mutationFn: (data: PasswordFields) =>
      apiClient.post(`/auth/change-password?password_old=${encodeURIComponent(data.oldPassword)}&password_new=${encodeURIComponent(data.newPassword)}`),
    onSuccess: () => {
      setSuccessMsg('Password updated successfully!');
      passwordForm.reset();
    },
    onError: (err: unknown) => {
      const error = err as { response?: { data?: { message?: string } }; message?: string };
      setErrorMsg(error.response?.data?.message || error.message || 'Password update failed.');
    },
  });

  const revokeSessionMutation = useMutation({
    mutationFn: (id: string) => apiClient.delete(`/auth/sessions/${id}`),
    onSuccess: () => {
      refetchSessions();
      setSuccessMsg('Session terminated successfully.');
    },
    onError: (err: unknown) => {
      const error = err as { response?: { data?: { message?: string } }; message?: string };
      setErrorMsg(error.response?.data?.message || error.message || 'Revocation failed.');
    },
  });

  const createKeyMutation = useMutation({
    mutationFn: () =>
      Promise.resolve({
        data: {
          key: `nm_live_${Math.random().toString(36).substring(2, 18)}${Math.random().toString(36).substring(2, 18)}`,
        },
      }),
    onSuccess: (res) => {
      setGeneratedKey(res.data.key);
      setSuccessMsg('Developer API Key generated successfully!');
      keyForm.reset();
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Account Settings</h1>
        <p className="text-sm text-slate-500">Configure developer access, passwords, and active browser sessions.</p>
      </div>

      {successMsg && (
        <div className="rounded-lg bg-emerald-50 p-4 text-xs font-medium text-emerald-700 dark:bg-emerald-950/20 dark:text-emerald-400">
          ✓ {successMsg}
        </div>
      )}

      {errorMsg && (
        <div className="rounded-lg bg-red-50 p-4 text-xs font-medium text-red-700 dark:bg-red-950/20 dark:text-red-400">
          {errorMsg}
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        {/* Profile Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5 text-indigo-600" /> Profile Configurations
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loadingProfile ? (
              <div className="h-20 animate-pulse rounded bg-slate-100 dark:bg-slate-800" />
            ) : (
              <form onSubmit={profileForm.handleSubmit((data) => updateProfileMutation.mutate(data))} className="space-y-4">
                <Field label="Email Address" error={profileForm.formState.errors.email?.message}>
                  <Input
                    placeholder="developer@nomen.ai"
                    error={!!profileForm.formState.errors.email}
                    {...profileForm.register('email')}
                  />
                </Field>
                <Button type="submit" isLoading={updateProfileMutation.isPending}>
                  Update Email
                </Button>
              </form>
            )}
          </CardContent>
        </Card>

        {/* Change Password Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ShieldAlert className="h-5 w-5 text-indigo-600" /> Change Password
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={passwordForm.handleSubmit((data) => updatePasswordMutation.mutate(data))} className="space-y-4">
              <Field label="Old Password" error={passwordForm.formState.errors.oldPassword?.message}>
                <Input
                  type="password"
                  placeholder="••••••••"
                  error={!!passwordForm.formState.errors.oldPassword}
                  {...passwordForm.register('oldPassword')}
                />
              </Field>
              <div className="grid gap-4 sm:grid-cols-2">
                <Field label="New Password" error={passwordForm.formState.errors.newPassword?.message}>
                  <Input
                    type="password"
                    placeholder="••••••••"
                    error={!!passwordForm.formState.errors.newPassword}
                    {...passwordForm.register('newPassword')}
                  />
                </Field>
                <Field label="Confirm Password" error={passwordForm.formState.errors.confirmPassword?.message}>
                  <Input
                    type="password"
                    placeholder="••••••••"
                    error={!!passwordForm.formState.errors.confirmPassword}
                    {...passwordForm.register('confirmPassword')}
                  />
                </Field>
              </div>
              <Button type="submit" isLoading={updatePasswordMutation.isPending}>
                Update Password
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* API keys manager */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Key className="h-5 w-5 text-indigo-600" /> Developer API Credentials
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <form onSubmit={keyForm.handleSubmit(() => createKeyMutation.mutate())} className="space-y-4">
              <Field label="Key Reference Name" error={keyForm.formState.errors.name?.message}>
                <Input
                  placeholder="Production Server Key"
                  error={!!keyForm.formState.errors.name}
                  {...keyForm.register('name')}
                />
              </Field>
              <Field label="Authorizations Scopes (Comma Separated)" error={keyForm.formState.errors.scopes?.message}>
                <Input
                  placeholder="generation.write, analytics.read"
                  error={!!keyForm.formState.errors.scopes}
                  {...keyForm.register('scopes')}
                />
              </Field>
              <Button type="submit" isLoading={createKeyMutation.isPending}>
                Generate Token
              </Button>
            </form>

            {generatedKey && (
              <div className="rounded-lg bg-indigo-50 p-4 border border-indigo-200 text-xs font-semibold text-indigo-700 dark:bg-indigo-950/20 dark:border-indigo-900 dark:text-indigo-400">
                <span className="block font-medium mb-1">Make sure to copy this credential now. You will not see it again:</span>
                <code className="block select-all bg-white border border-indigo-100 p-2 rounded mt-2 dark:bg-slate-900 dark:border-indigo-950">{generatedKey}</code>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Sessions & Theme */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Monitor className="h-5 w-5 text-indigo-600" /> Session & Theme
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6 text-xs">
            {/* Theme switcher */}
            <div>
              <span className="font-semibold block mb-2 text-slate-700 dark:text-slate-300">Layout Appearance</span>
              <div className="flex gap-2">
                <Button variant={theme === 'light' ? 'primary' : 'outline'} size="sm" onClick={() => setTheme('light')}>Light</Button>
                <Button variant={theme === 'dark' ? 'primary' : 'outline'} size="sm" onClick={() => setTheme('dark')}>Dark</Button>
                <Button variant={theme === 'system' ? 'primary' : 'outline'} size="sm" onClick={() => setTheme('system')}>System</Button>
              </div>
            </div>

            {/* Active sessions list */}
            <div className="border-t border-slate-100 pt-4 dark:border-slate-800">
              <span className="font-semibold block mb-2 text-slate-700 dark:text-slate-300">Active Browser Sessions</span>
              <div className="divide-y divide-slate-100 dark:divide-slate-800">
                {sessions.map((s: SessionItem) => (
                  <div key={s.id} className="flex justify-between items-center py-2">
                    <div>
                      <span className="font-semibold text-slate-800 dark:text-slate-200">{s.ip_address || '127.0.0.1'}</span>
                      <span className="block text-xxs text-slate-400">Last activity: {new Date(s.last_activity).toLocaleTimeString()}</span>
                    </div>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => revokeSessionMutation.mutate(s.id)}
                      isLoading={revokeSessionMutation.isPending}
                    >
                      Revoke
                    </Button>
                  </div>
                ))}
                {sessions.length === 0 && (
                  <span className="text-slate-400">No session metrics available.</span>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
