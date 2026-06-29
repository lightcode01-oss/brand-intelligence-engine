'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as zod from 'zod';
import Link from 'next/link';
import { apiClient } from '@/lib/api/client';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Field } from '@/components/forms/Field';
import { Search, Trash2, ArrowRight, Sparkles } from 'lucide-react';

interface ProjectItem {
  id: string;
  workspace_id: string;
  prompt: string;
  target_syllables: number;
  selected_tlds: string[];
}

const projectSchema = zod.object({
  prompt: zod.string().min(5, 'Concept concept must be at least 5 characters long'),
  target_syllables: zod.coerce.number().min(1, 'At least 1 syllable').max(5, 'At most 5 syllables'),
  selected_tlds: zod.string().min(1, 'TLD extensions required (e.g. .com, .io)'),
});

type ProjectFields = zod.infer<typeof projectSchema>;

export default function ProjectsPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // 1. Fetch active projects list
  const { data: projectsResponse, isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: () => apiClient.get('/projects/').then((res) => res.data),
  });

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ProjectFields>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      prompt: '',
      target_syllables: 2,
      selected_tlds: '.com, .io',
    },
  });

  // 2. Mutations
  const createMutation = useMutation({
    mutationFn: (data: ProjectFields) => {
      const tlds = data.selected_tlds
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean);
      return apiClient.post('/projects/', {
        workspace_id: '00000000-0000-0000-0000-000000000000',
        prompt: data.prompt,
        target_syllables: data.target_syllables,
        selected_tlds: tlds,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      setSuccessMsg('Project created successfully!');
      reset();
    },
    onError: (err: unknown) => {
      const error = err as { response?: { data?: { message?: string } }; message?: string };
      setErrorMsg(error.response?.data?.message || error.message || 'Project creation failed.');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => apiClient.delete(`/projects/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      setSuccessMsg('Project deleted successfully!');
    },
    onError: (err: unknown) => {
      const error = err as { response?: { data?: { message?: string } }; message?: string };
      setErrorMsg(error.response?.data?.message || error.message || 'Deletion failed.');
    },
  });

  const projects: ProjectItem[] = projectsResponse?.data?.items || [];
  
  // Filter search matches
  const filteredProjects = projects.filter((p: ProjectItem) =>
    p.prompt.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Brainstorming Projects</h1>
          <p className="text-sm text-slate-500">Organize names clearance projects and configuration matrices.</p>
        </div>
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

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Create inline Form card */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-indigo-600" /> Start Naming Concept
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit((data) => createMutation.mutate(data))} className="space-y-4">
              <Field label="Brand Description Concept" error={errors.prompt?.message}>
                <textarea
                  className="flex min-h-[80px] w-full rounded-lg border border-slate-200 bg-transparent px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600 dark:border-slate-800 dark:text-white"
                  placeholder="AI-powered naming clearance system for startup businesses"
                  {...register('prompt')}
                />
              </Field>
              <Field label="Target Syllables count" error={errors.target_syllables?.message}>
                <Input
                  type="number"
                  placeholder="2"
                  error={!!errors.target_syllables}
                  {...register('target_syllables')}
                />
              </Field>
              <Field label="Extensions (Comma Separated)" error={errors.selected_tlds?.message}>
                <Input
                  placeholder=".com, .io, .co"
                  error={!!errors.selected_tlds}
                  {...register('selected_tlds')}
                />
              </Field>
              <Button type="submit" className="w-full" isLoading={isSubmitting}>
                Create Project
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Projects List view */}
        <div className="lg:col-span-2 space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
            <Input
              type="text"
              placeholder="Search projects..."
              className="pl-9"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          {isLoading ? (
            <div className="flex flex-col gap-2">
              <div className="h-16 animate-pulse rounded bg-slate-100 dark:bg-slate-800" />
              <div className="h-16 animate-pulse rounded bg-slate-100 dark:bg-slate-800" />
            </div>
          ) : filteredProjects.length === 0 ? (
            <div className="rounded-xl border border-dashed border-slate-200 py-12 text-center text-sm text-slate-500 dark:border-slate-800">
              No matching projects found.
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2">
              {filteredProjects.map((proj: ProjectItem) => (
                <Card key={proj.id} className="hover:border-indigo-500/50 transition-all">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-semibold truncate">
                      {proj.prompt}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3 pb-4 text-xs text-slate-500">
                    <div className="flex justify-between">
                      <span>Syllables:</span>
                      <span className="font-semibold text-slate-700 dark:text-slate-300">{proj.target_syllables}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Extensions:</span>
                      <span className="font-semibold text-slate-700 dark:text-slate-300">{proj.selected_tlds.join(', ')}</span>
                    </div>
                    <div className="flex gap-2 pt-2 border-t border-slate-100 dark:border-slate-800">
                      <Link href={`/dashboard/projects/${proj.id}/generate`} className="flex-1">
                        <Button variant="primary" className="w-full flex items-center justify-center gap-1" size="sm">
                          Generate <ArrowRight className="h-3 w-3" />
                        </Button>
                      </Link>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => {
                          if (confirm('Delete this project?')) {
                            deleteMutation.mutate(proj.id);
                          }
                        }}
                        isLoading={deleteMutation.isPending}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
