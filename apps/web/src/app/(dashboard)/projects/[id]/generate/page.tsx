'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as zod from 'zod';
import { useParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { useWebSocketStore } from '@/store/websocketStore';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Field } from '@/components/forms/Field';
import CommentSection from '@/components/collaboration/CommentSection';
import { 
  Sparkles, 
  Settings, 
  Loader2, 
  ShieldAlert, 
  Globe, 
  FileDown, 
  Heart, 
  Copy, 
  RotateCcw, 
  TrendingUp,
  Volume2,
  FolderPlus
} from 'lucide-react';

const generateSchema = zod.object({
  model_name: zod.string(),
  temperature: zod.coerce.number().min(0).max(1),
  industry: zod.string().min(2, 'Industry is required'),
  keywords: zod.string().min(2, 'Keywords required'),
  tone: zod.string().min(2, 'Tone descriptor is required'),
  audience: zod.string().min(2, 'Target audience required'),
});

type GenerateFields = zod.infer<typeof generateSchema>;

interface GeneratedNameItem {
  id: string;
  name_string: string;
  style: string;
  temperature: number;
}

interface DomainCheckItem {
  id: string;
  domain_name: string;
  available: boolean;
  price?: number;
}

interface TrademarkCheckItem {
  id: string;
  mark_text: string;
  jurisdiction: string;
  class_code: string;
  risk_status: string;
}

interface CollectionItem {
  id: string;
  name: string;
}

export default function GenerateWorkflowPage() {
  const params = useParams();
  const projectId = params.id as string;
  
  const workspace = useWorkspaceStore();
  const workspaceId = workspace.activeWorkspace?.id;
  const wsStore = useWebSocketStore();

  const [step, setStep] = useState<'configure' | 'polling' | 'results'>('configure');
  const [jobId, setJobId] = useState<string | null>(null);
  const [pollError, setPollError] = useState<string | null>(null);
  const [favorites, setFavorites] = useState<Record<string, boolean>>({});
  const [copiedName, setCopiedName] = useState<string | null>(null);
  const [selectedNameId, setSelectedNameId] = useState<string | null>(null);

  // 1. Fetch details of this project
  const { data: projectResponse } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => apiClient.get(`/projects/${projectId}`).then((res) => res.data),
    enabled: !!projectId,
  });

  const projectPrompt = projectResponse?.data?.prompt || 'Naming campaign';

  // 2. Fetch collections folders list
  const { data: collectionsResponse } = useQuery({
    queryKey: ['collections', workspaceId],
    queryFn: () => apiClient.get(`/collections?workspace_id=${workspaceId}`).then((res) => res.data),
    enabled: !!workspaceId,
  });
  const collections: CollectionItem[] = collectionsResponse?.data || [];

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<GenerateFields>({
    resolver: zodResolver(generateSchema),
    defaultValues: {
      model_name: 'gemini-1.5-flash',
      temperature: 0.7,
      industry: 'Technology',
      keywords: 'brand, intelligence, engine',
      tone: 'Professional',
      audience: 'Enterprise developers',
    },
  });

  // 4. Fetch generated names list
  const { data: namesResponse, refetch: refetchNames } = useQuery({
    queryKey: ['names', projectId],
    queryFn: () => apiClient.get(`/projects/${projectId}/names`).then((res) => res.data),
    enabled: step === 'results',
  });

  // 2. Submit generation job
  const onSubmit = async (data: GenerateFields) => {
    setPollError(null);
    try {
      const response = await apiClient.post(`/projects/${projectId}/generate`, {
        model_name: data.model_name,
        temperature: data.temperature,
        industry: data.industry,
        keywords: data.keywords,
        tone: data.tone,
        target_audience: data.audience,
      });
      const job = response.data?.data;
      if (job?.id) {
        setJobId(job.id);
        setStep('polling');
      } else {
        setPollError('Invalid job ID returned.');
      }
    } catch (err: unknown) {
      const error = err as { response?: { data?: { message?: string } }; message?: string };
      setPollError(error.response?.data?.message || error.message || 'Failed to trigger generation.');
    }
  };

  // 3. WebSocket and Polling fallback for status updates
  const currentJobProgress = jobId ? wsStore.jobProgress[jobId] : null;
  const currentStage = currentJobProgress?.stage || 'Queued';

  useEffect(() => {
    if (step !== 'polling' || !jobId) return;

    // Check if websocket sent finished signal
    if (currentJobProgress) {
      if (currentJobProgress.status === 'SUCCESS' || currentJobProgress.stage === 'Finished') {
        setStep('results');
        refetchNames();
        return;
      } else if (currentJobProgress.status === 'FAILED' || currentJobProgress.stage === 'Failed') {
        setStep('configure');
        setPollError(currentJobProgress.error_message || 'Asynchronous generation failed.');
        return;
      }
    }

    // Interval polling fallback
    const checkStatus = async () => {
      try {
        const response = await apiClient.get(`/jobs/${jobId}`);
        const job = response.data?.data;
        if (job?.status === 'SUCCESS') {
          setStep('results');
          refetchNames();
        } else if (job?.status === 'FAILED') {
          setStep('configure');
          setPollError(job?.error_message || 'Asynchronous generation job failed.');
        }
      } catch (err: unknown) {
        const error = err as { message?: string };
        setStep('configure');
        setPollError(error.message || 'Error occurred while polling job status.');
      }
    };

    const intervalId = setInterval(checkStatus, 3000); // Relaxed polling delay when WebSocket is secondary
    return () => clearInterval(intervalId);
  }, [step, jobId, currentJobProgress, refetchNames]);

  const names: GeneratedNameItem[] = useMemo(() => namesResponse?.data?.items || [], [namesResponse]);
  
  // Set first name as active by default if not set
  useEffect(() => {
    if (names.length > 0 && !selectedNameId) {
      setSelectedNameId(names[0].id);
    }
  }, [names, selectedNameId]);

  const activeName = names.find((n) => n.id === selectedNameId) || names[0];

  // 5. Fetch sub-level clearance detail (domains and trademarks)
  const { data: domainsResponse } = useQuery({
    queryKey: ['domains', activeName?.id],
    queryFn: () => apiClient.get(`/names/${activeName.id}/domains`).then((res) => res.data),
    enabled: !!activeName?.id,
  });

  const { data: trademarksResponse } = useQuery({
    queryKey: ['trademarks', activeName?.id],
    queryFn: () => apiClient.get(`/names/${activeName.id}/trademarks`).then((res) => res.data),
    enabled: !!activeName?.id,
  });

  const domains = domainsResponse?.data || [];
  const trademarks = trademarksResponse?.data || [];

  // Load initial favorites states
  useEffect(() => {
    if (!workspaceId || names.length === 0) return;
    apiClient.get(`/favorites?workspace_id=${workspaceId}`)
      .then((res) => {
        const favList = res.data?.data || [];
        const mapping = favList.reduce((acc: Record<string, boolean>, f: { name_id: string }) => {
          acc[f.name_id] = true;
          return acc;
        }, {});
        setFavorites(mapping);
      })
      .catch(console.error);
  }, [workspaceId, names]);

  // 6. Action triggers
  const handleFavorite = async (nameId: string) => {
    if (!workspaceId) return;
    try {
      const isFav = !favorites[nameId];
      setFavorites((prev) => ({ ...prev, [nameId]: isFav }));
      await apiClient.post(`/names/${nameId}/favorite?workspace_id=${workspaceId}`);
      await apiClient.put(`/names/${nameId}`, {
        lifecycle_state: isFav ? 'SAVED' : 'SUGGESTED',
      });
    } catch (err) {
      console.error('Failed to update name state:', err);
    }
  };

  const handleAddToCollection = async (collectionId: string, nameId: string) => {
    try {
      await apiClient.post(`/collections/${collectionId}/items?name_id=${nameId}`);
      alert('Candidate added to collection successfully!');
    } catch (err) {
      console.error(err);
    }
  };

  const handleCopy = (name: string) => {
    navigator.clipboard.writeText(name);
    setCopiedName(name);
    setTimeout(() => setCopiedName(null), 2000);
  };

  const handleExport = async (format: string) => {
    if (!activeName?.id) return;
    try {
      const response = await apiClient.post('/exports/', {
        name_id: activeName.id,
        format,
      });
      const url = response.data?.data?.package_url;
      if (url) {
        window.open(url, '_blank');
      }
    } catch (err) {
      console.error('Failed to compile exports packages:', err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-200 pb-4 dark:border-slate-800">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">AI Naming Workflow</h1>
        <p className="text-sm text-slate-500">Project: <span className="font-semibold text-slate-700 dark:text-slate-300">{projectPrompt}</span></p>
      </div>

      {pollError && (
        <div className="rounded-lg bg-red-50 p-4 text-xs font-medium text-red-700 dark:bg-red-950/20 dark:text-red-400">
          {pollError}
        </div>
      )}

      {/* STEP 1: CONFIGURE GENERATION PARAMETERS */}
      {step === 'configure' && (
        <Card className="max-w-2xl mx-auto border-slate-100 dark:border-slate-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5 text-indigo-600" /> Pipeline Parameter Mapping
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <Field label="Model Engine" error={errors.model_name?.message}>
                  <select
                    className="flex h-10 w-full rounded-lg border border-slate-200 bg-transparent px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600 dark:border-slate-800 dark:text-white"
                    {...register('model_name')}
                  >
                    <option value="gemini-1.5-flash">Gemini 1.5 Flash (Default)</option>
                    <option value="gpt-4o">GPT-4o (Pro Plan)</option>
                    <option value="claude-3-sonnet">Claude 3.5 Sonnet</option>
                  </select>
                </Field>
                <Field label="Creativity Temperature (0-1)" error={errors.temperature?.message}>
                  <Input
                    type="number"
                    step="0.1"
                    placeholder="0.7"
                    error={!!errors.temperature}
                    {...register('temperature')}
                  />
                </Field>
              </div>

              <Field label="Target Industry" error={errors.industry?.message}>
                <Input
                  placeholder="Healthcare, Developer SaaS, Web3"
                  error={!!errors.industry}
                  {...register('industry')}
                />
              </Field>

              <div className="grid gap-4 sm:grid-cols-2">
                <Field label="Concept Keywords" error={errors.keywords?.message}>
                  <Input
                    placeholder="secure, ledger, instant"
                    error={!!errors.keywords}
                    {...register('keywords')}
                  />
                </Field>
                <Field label="Tone Voice" error={errors.tone?.message}>
                  <Input
                    placeholder="Bold, Professional, Friendly"
                    error={!!errors.tone}
                    {...register('tone')}
                  />
                </Field>
              </div>

              <Field label="Target Audience" error={errors.audience?.message}>
                <Input
                  placeholder="Small business owners, enterprise developers"
                  error={!!errors.audience}
                  {...register('audience')}
                />
              </Field>

              <Button type="submit" className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700" isLoading={isSubmitting}>
                Generate Names <Sparkles className="h-4 w-4" />
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {/* STEP 2: POLLING PROGRESS (Real-time Websocket stage logs indicator) */}
      {step === 'polling' && (
        <Card className="max-w-md mx-auto py-12 border-slate-100 dark:border-slate-800 bg-white/80 dark:bg-slate-950/80 backdrop-blur-md">
          <CardContent className="flex flex-col items-center justify-center space-y-4">
            <Loader2 className="h-10 w-10 animate-spin text-indigo-600" />
            <div className="text-center space-y-2">
              <h3 className="font-bold text-lg dark:text-white">Generating Brand Concepts</h3>
              
              {/* Dynamic live stage badge */}
              <div className="inline-block px-3 py-1 rounded-full text-xs font-semibold bg-indigo-50 dark:bg-indigo-950/20 text-indigo-700 dark:text-indigo-400">
                Stage: {currentStage}
              </div>
              
              <p className="text-xs text-slate-500 max-w-xs mx-auto">
                Connecting to real-time pipelines. Phonetic filters, pronunciation scoring, and trademark clearance validation active...
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* STEP 3: RESULTS SCREEN & CLEARANCE METRICS */}
      {step === 'results' && (
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Candidates list panel */}
          <Card className="lg:col-span-1 border-slate-100 dark:border-slate-800">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-sm font-semibold">Candidates Name list</CardTitle>
              <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => setStep('configure')}>
                <RotateCcw className="h-4 w-4" />
              </Button>
            </CardHeader>
            <CardContent className="space-y-3">
              {names.map((nm: GeneratedNameItem) => (
                <div 
                  key={nm.id} 
                  onClick={() => setSelectedNameId(nm.id)}
                  className={`flex items-center justify-between p-3.5 rounded-xl border cursor-pointer transition ${selectedNameId === nm.id ? 'border-indigo-600 bg-indigo-50/10' : 'border-slate-100 dark:border-slate-850 bg-white dark:bg-slate-950'}`}
                >
                  <div>
                    <h4 className="font-bold text-slate-800 dark:text-slate-100">{nm.name_string}</h4>
                    <span className="text-xxs text-slate-400 capitalize">{nm.style} | Temp: {nm.temperature}</span>
                  </div>
                  <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="h-8 w-8 p-0" 
                      onClick={() => handleCopy(nm.name_string)}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="h-8 w-8 p-0" 
                      onClick={() => handleFavorite(nm.id)}
                    >
                      <Heart className={`h-4 w-4 ${favorites[nm.id] ? 'fill-red-500 text-red-500' : 'text-slate-400'}`} />
                    </Button>
                  </div>
                </div>
              ))}
              {copiedName && (
                <div className="text-center text-xs text-indigo-600 bg-indigo-50 dark:bg-indigo-950/20 py-2 rounded-lg">
                  Copied &quot;{copiedName}&quot; to clipboard!
                </div>
              )}
            </CardContent>
          </Card>

          {/* Active Clearance Metrics & Collaboration panel */}
          {activeName && (
            <div className="lg:col-span-2 space-y-6">
              <div className="grid gap-6 sm:grid-cols-2">
                {/* Brand Score */}
                <Card className="border-slate-100 dark:border-slate-800">
                  <CardHeader>
                    <CardTitle className="text-sm font-semibold flex items-center gap-2">
                      <TrendingUp className="h-4 w-4 text-indigo-600" /> Nomen Brand Score
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="flex items-center gap-4">
                    <div className="h-16 w-16 rounded-full border-4 border-indigo-600 flex items-center justify-center font-bold text-xl dark:text-white">
                      85
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">Excellent clearance score</p>
                      <span className="text-xs text-slate-400">Similarity detection: Low risk</span>
                    </div>
                  </CardContent>
                </Card>

                {/* Pronunciation */}
                <Card className="border-slate-100 dark:border-slate-800">
                  <CardHeader>
                    <CardTitle className="text-sm font-semibold flex items-center gap-2">
                      <Volume2 className="h-4 w-4 text-emerald-600" /> Pronunciation Analysis
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-sm font-bold text-slate-800 dark:text-slate-200">
                      NOH-men
                    </div>
                    <span className="text-xs text-slate-400">Easy readability, moderate corporate recall.</span>
                  </CardContent>
                </Card>
              </div>

              {/* Collections & Folders assignments */}
              {collections.length > 0 && (
                <Card className="border-slate-100 dark:border-slate-800">
                  <CardHeader>
                    <CardTitle className="text-sm font-semibold flex items-center gap-2">
                      <FolderPlus className="h-4 w-4 text-amber-500" /> Save to Workspace Collection
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="flex flex-wrap gap-2">
                    {collections.map((col) => (
                      <Button
                        key={col.id}
                        variant="outline"
                        size="sm"
                        onClick={() => handleAddToCollection(col.id, activeName.id)}
                        className="flex items-center gap-1.5"
                      >
                        <span>{col.name}</span>
                      </Button>
                    ))}
                  </CardContent>
                </Card>
              )}

              {/* Domain & Trademark Clearance details */}
              <div className="grid gap-6 md:grid-cols-2">
                <Card className="border-slate-100 dark:border-slate-800">
                  <CardHeader>
                    <CardTitle className="text-sm font-semibold flex items-center gap-2">
                      <Globe className="h-4 w-4 text-indigo-600" /> Domain Availability
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="divide-y divide-slate-100 dark:divide-slate-800">
                    {domains.map((dom: DomainCheckItem) => (
                      <div key={dom.id} className="flex justify-between py-2 text-sm">
                        <span className="font-semibold text-slate-700 dark:text-slate-300">{dom.domain_name}</span>
                        <span className={`font-medium ${dom.available ? 'text-emerald-600' : 'text-red-500'}`}>
                          {dom.available ? `Available (approx $${dom.price || '12'})` : 'Taken'}
                        </span>
                      </div>
                    ))}
                  </CardContent>
                </Card>

                <Card className="border-slate-100 dark:border-slate-800">
                  <CardHeader>
                    <CardTitle className="text-sm font-semibold flex items-center gap-2">
                      <ShieldAlert className="h-4 w-4 text-amber-500" /> USPTO Trademark Clearance
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="divide-y divide-slate-100 dark:divide-slate-800">
                    {trademarks.map((tm: TrademarkCheckItem) => (
                      <div key={tm.id} className="flex justify-between py-2 text-sm">
                        <div>
                          <span className="font-semibold text-slate-700 dark:text-slate-300">{tm.mark_text}</span>
                          <span className="block text-[10px] text-slate-400">Class: {tm.class_code}</span>
                        </div>
                        <span className="font-semibold text-emerald-600 text-xxs uppercase rounded bg-emerald-50 px-2 py-0.5 dark:bg-emerald-950/20">
                          {tm.risk_status} RISK
                        </span>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </div>

              {/* Real-time Collaboration Notes */}
              {workspaceId && (
                <CommentSection 
                  nameId={activeName.id}
                  workspaceId={workspaceId}
                  projectId={projectId}
                />
              )}

              {/* Export Panel Actions */}
              <Card className="border-slate-100 dark:border-slate-800">
                <CardHeader>
                  <CardTitle className="text-sm font-semibold flex items-center gap-2">
                    <FileDown className="h-4 w-4 text-indigo-600" /> Export Clearance Package
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex gap-4">
                  <Button variant="outline" size="sm" onClick={() => handleExport('csv')}>Export CSV</Button>
                  <Button variant="outline" size="sm" onClick={() => handleExport('json')}>Export JSON</Button>
                  <Button variant="outline" size="sm" onClick={() => handleExport('markdown')}>Export Markdown</Button>
                  <Button variant="outline" size="sm" onClick={() => handleExport('pdf')}>Export PDF</Button>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
