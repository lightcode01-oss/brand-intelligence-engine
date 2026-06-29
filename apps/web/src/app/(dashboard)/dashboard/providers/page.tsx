'use client';

import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { ArrowUp, ArrowDown, Shield } from 'lucide-react';

interface ProviderRoute {
  name: string;
  slug: string;
  priority: number;
  health: 'Healthy' | 'Degraded' | 'Open (Circuit)';
  cost: string;
}

export default function ProvidersPage() {
  const [loading, setLoading] = useState(false);
  const [providers, setProviders] = useState<ProviderRoute[]>([
    { name: 'Google Gemini 1.5 Flash', slug: 'gemini', priority: 1, health: 'Healthy', cost: '$0.00035 / 1k' },
    { name: 'OpenAI GPT-4o', slug: 'openai', priority: 2, health: 'Healthy', cost: '$0.00500 / 1k' },
    { name: 'Anthropic Claude 3.5 Sonnet', slug: 'claude', priority: 3, health: 'Healthy', cost: '$0.00300 / 1k' },
    { name: 'Local Ollama Model (Llama-3)', slug: 'ollama', priority: 4, health: 'Healthy', cost: '$0.00000 (Free)' }
  ]);

  const handleMove = (index: number, direction: 'up' | 'down') => {
    const nextIndex = direction === 'up' ? index - 1 : index + 1;
    if (nextIndex < 0 || nextIndex >= providers.length) return;
    
    const newProviders = [...providers];
    const temp = newProviders[index];
    newProviders[index] = newProviders[nextIndex];
    newProviders[nextIndex] = temp;
    
    // Update priorities
    newProviders.forEach((p, idx) => {
      p.priority = idx + 1;
    });
    
    setProviders(newProviders);
  };

  const handleSaveOrder = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      alert('AI Provider routing priorities saved successfully.');
    }, 500);
  };

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">AI Routing Priorities</h1>
          <p className="text-sm text-slate-500">
            Reorder routing priority list to coordinate dynamic LLM fallback and circuit-breaker switches.
          </p>
        </div>
        <Button variant="primary" size="sm" onClick={handleSaveOrder} disabled={loading}>
          {loading ? 'Saving...' : 'Save Priority Order'}
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base font-bold flex items-center gap-2">
            <Shield className="h-5 w-5 text-indigo-600" />
            Active LLM Providers
          </CardTitle>
        </CardHeader>
        <CardContent className="divide-y divide-slate-100 dark:divide-slate-800">
          {providers.map((p, index) => (
            <div key={p.slug} className="flex items-center justify-between py-4 first:pt-0 last:pb-0 gap-4">
              <div className="flex items-center gap-3">
                <span className="text-sm font-bold text-slate-400">#{p.priority}</span>
                <div>
                  <h4 className="text-sm font-bold text-slate-900 dark:text-white">{p.name}</h4>
                  <p className="text-[10px] text-slate-400 mt-0.5">Est. Input cost: {p.cost}</p>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1.5">
                  <span className="h-2.5 w-2.5 bg-emerald-500 rounded-full animate-pulse" />
                  <span className="text-xs font-semibold text-slate-600 dark:text-slate-300">{p.health}</span>
                </div>

                <div className="flex items-center bg-slate-50 dark:bg-slate-850 p-1 rounded-md border border-slate-200/50">
                  <button
                    disabled={index === 0}
                    onClick={() => handleMove(index, 'up')}
                    className="p-1 text-slate-400 hover:text-slate-700 disabled:opacity-30"
                  >
                    <ArrowUp className="h-4 w-4" />
                  </button>
                  <button
                    disabled={index === providers.length - 1}
                    onClick={() => handleMove(index, 'down')}
                    className="p-1 text-slate-400 hover:text-slate-700 disabled:opacity-30"
                  >
                    <ArrowDown className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
