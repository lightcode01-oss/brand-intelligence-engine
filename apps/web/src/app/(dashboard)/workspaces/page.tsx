'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as zod from 'zod';
import { apiClient } from '@/lib/api/client';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Field } from '@/components/forms/Field';
import { Plus, Settings, Trash, Shield } from 'lucide-react';

const workspaceSchema = zod.object({
  display_name: zod.string().min(2, 'Display name must be at least 2 characters'),
  slug: zod.string().min(2, 'Slug must be at least 2 characters').regex(/^[a-z0-9-]+$/, 'Slug must be alphanumeric/dashes'),
});

const inviteMemberSchema = zod.object({
  email: zod.string().email('Please enter a valid email address'),
  role: zod.enum(['MEMBER', 'ADMIN']),
});

type WorkspaceFields = zod.infer<typeof workspaceSchema>;
type InviteMemberFields = zod.infer<typeof inviteMemberSchema>;

export default function WorkspacesPage() {
  const queryClient = useQueryClient();
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // 1. Fetch active workspaces
  const { data: workspacesResponse, isLoading } = useQuery({
    queryKey: ['workspaces'],
    queryFn: () => apiClient.get('/workspaces/').then((res) => res.data),
  });

  const workspaces = workspacesResponse?.data?.items || [];
  const activeWorkspace = workspaces[0];

  // 2. React Hook Forms
  const workspaceForm = useForm<WorkspaceFields>({
    resolver: zodResolver(workspaceSchema),
    defaultValues: {
      display_name: activeWorkspace?.display_name || '',
      slug: activeWorkspace?.slug || '',
    },
  });

  const createForm = useForm<WorkspaceFields>({
    resolver: zodResolver(workspaceSchema),
    defaultValues: {
      display_name: '',
      slug: '',
    },
  });

  const memberForm = useForm<InviteMemberFields>({
    resolver: zodResolver(inviteMemberSchema),
    defaultValues: {
      email: '',
      role: 'MEMBER',
    },
  });

  // 3. Mutations
  const createMutation = useMutation({
    mutationFn: (data: WorkspaceFields) => apiClient.post('/workspaces/', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspaces'] });
      setSuccessMsg('Workspace created successfully!');
      createForm.reset();
    },
    onError: (err: unknown) => {
      const error = err as { response?: { data?: { message?: string } }; message?: string };
      setErrorMsg(error.response?.data?.message || error.message || 'Creation failed.');
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: WorkspaceFields) => apiClient.put(`/workspaces/${activeWorkspace?.id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspaces'] });
      setSuccessMsg('Workspace renamed successfully!');
    },
    onError: (err: unknown) => {
      const error = err as { response?: { data?: { message?: string } }; message?: string };
      setErrorMsg(error.response?.data?.message || error.message || 'Rename failed.');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => apiClient.delete(`/workspaces/${activeWorkspace?.id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspaces'] });
      setSuccessMsg('Workspace deleted successfully!');
    },
    onError: (err: unknown) => {
      const error = err as { response?: { data?: { message?: string } }; message?: string };
      setErrorMsg(error.response?.data?.message || error.message || 'Deletion failed.');
    },
  });

  const inviteMutation = useMutation({
    mutationFn: (data: InviteMemberFields) =>
      apiClient.post(`/workspaces/${activeWorkspace?.id}/members`, {
        user_id: '00000000-0000-0000-0000-000000000000', // Mock static target
        role: data.role,
      }),
    onSuccess: () => {
      setSuccessMsg('Invitation sent successfully!');
      memberForm.reset();
    },
    onError: (err: unknown) => {
      const error = err as { response?: { data?: { message?: string } }; message?: string };
      setErrorMsg(error.response?.data?.message || error.message || 'Invitation failed.');
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Workspace Settings</h1>
        <p className="text-sm text-slate-500">Configure team access, branding configurations, and names clearance pipelines.</p>
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
        {/* Create Workspace details */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Plus className="h-5 w-5 text-indigo-600" /> Create Workspace
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={createForm.handleSubmit((data) => createMutation.mutate(data))} className="space-y-4">
              <Field label="Display Name" error={createForm.formState.errors.display_name?.message}>
                <Input
                  placeholder="Marketing Team Workspace"
                  error={!!createForm.formState.errors.display_name}
                  {...createForm.register('display_name')}
                />
              </Field>
              <Field label="Workspace Slug" error={createForm.formState.errors.slug?.message}>
                <Input
                  placeholder="marketing-team"
                  error={!!createForm.formState.errors.slug}
                  {...createForm.register('slug')}
                />
              </Field>
              <Button type="submit" isLoading={createMutation.isPending}>
                Create Workspace
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Workspace details and updates */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5 text-slate-500" /> Rename Workspace
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-24 animate-pulse rounded bg-slate-100 dark:bg-slate-800" />
            ) : (
              <form onSubmit={workspaceForm.handleSubmit((data) => updateMutation.mutate(data))} className="space-y-4">
                <Field label="Display Name" error={workspaceForm.formState.errors.display_name?.message}>
                  <Input
                    placeholder="Engineering Division"
                    error={!!workspaceForm.formState.errors.display_name}
                    {...workspaceForm.register('display_name')}
                  />
                </Field>
                <Field label="Workspace Slug" error={workspaceForm.formState.errors.slug?.message}>
                  <Input
                    placeholder="eng-division"
                    error={!!workspaceForm.formState.errors.slug}
                    {...workspaceForm.register('slug')}
                  />
                </Field>
                <div className="flex gap-4">
                  <Button type="submit" isLoading={updateMutation.isPending}>
                    Save Changes
                  </Button>
                  {activeWorkspace && (
                    <Button
                      type="button"
                      variant="destructive"
                      className="flex items-center gap-2"
                      onClick={() => {
                        if (confirm('Are you sure you want to delete this workspace?')) {
                          deleteMutation.mutate();
                        }
                      }}
                      isLoading={deleteMutation.isPending}
                    >
                      <Trash className="h-4 w-4" /> Delete Workspace
                    </Button>
                  )}
                </div>
              </form>
            )}
          </CardContent>
        </Card>

        {/* Invite members */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-slate-500" /> Invite Team Member
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={memberForm.handleSubmit((data) => inviteMutation.mutate(data))} className="space-y-4">
              <Field label="Member Email Address" error={memberForm.formState.errors.email?.message}>
                <Input
                  placeholder="collaborator@company.com"
                  error={!!memberForm.formState.errors.email}
                  {...memberForm.register('email')}
                />
              </Field>
              <Field label="Permission Role" error={memberForm.formState.errors.role?.message}>
                <select
                  className="flex h-10 w-full rounded-lg border border-slate-200 bg-transparent px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600 dark:border-slate-800 dark:text-white"
                  {...memberForm.register('role')}
                >
                  <option value="MEMBER">MEMBER</option>
                  <option value="ADMIN">ADMIN</option>
                </select>
              </Field>
              <Button type="submit" className="w-full flex items-center justify-center gap-2" isLoading={inviteMutation.isPending}>
                <Plus className="h-4 w-4" /> Send Invite
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
