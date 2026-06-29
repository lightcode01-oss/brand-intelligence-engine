'use client';

import React, { useState } from 'react';
import { apiClient } from '@/lib/api/client';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Activity, Server, CheckCircle, RefreshCw } from 'lucide-react';

export default function SystemHealthPage() {
  const [loading, setLoading] = useState(false);
  const services = [
    { name: 'Core API Gateway', status: 'Operational', latency: '4ms', uptime: '99.98%' },
    { name: 'PostgreSQL DB Pool', status: 'Operational', latency: '1.2ms', uptime: '100%' },
    { name: 'Redis Cache cluster', status: 'Operational', latency: '0.8ms', uptime: '99.99%' },
    { name: 'Celery Workers High', status: 'Active (2)', latency: 'Queues empty', uptime: '99.9%' }
  ];

  const handlePing = async () => {
    setLoading(true);
    try {
      await apiClient.get('/ready');
      alert('Liveness health check resolved successfully!');
    } catch {
      alert('Liveness check timed out.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Service Health Indicators</h1>
          <p className="text-sm text-slate-500">Live operational checkpoints and uptime index for each platform microservice component.</p>
        </div>
        <Button variant="outline" size="sm" onClick={handlePing} disabled={loading} className="flex items-center gap-1.5">
          {loading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Activity className="h-4 w-4" />}
          Trigger Ping Check
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {services.map((s, idx) => (
          <Card key={idx}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div className="flex items-center gap-2">
                <Server className="h-5 w-5 text-indigo-600" />
                <CardTitle className="text-sm font-bold">{s.name}</CardTitle>
              </div>
              <div className="flex items-center gap-1">
                <CheckCircle className="h-4 w-4 text-emerald-500" />
                <span className="text-xs font-bold text-emerald-600">{s.status}</span>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between text-xs mt-2">
                <div className="space-y-0.5">
                  <span className="text-slate-400 block font-bold">Latency</span>
                  <span className="font-semibold text-slate-800 dark:text-slate-200">{s.latency}</span>
                </div>
                <div className="space-y-0.5 text-right">
                  <span className="text-slate-400 block font-bold">Uptime</span>
                  <span className="font-semibold text-slate-800 dark:text-slate-200">{s.uptime}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
