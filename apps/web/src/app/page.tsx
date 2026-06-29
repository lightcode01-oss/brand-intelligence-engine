'use client';

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

export default function Home() {
  return (
    <main className="flex min-h-screen items-center justify-center p-6 bg-slate-50 dark:bg-slate-900 transition-colors duration-300">
      <Card className="w-full max-w-md p-4">
        <CardHeader>
          <CardTitle>Nomen Brand Platform</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Phase 3.1 Frontend Design System Foundation Active.
          </p>
          <div className="flex gap-4 pt-2">
            <Button variant="primary">Primary Action</Button>
            <Button variant="secondary">Secondary</Button>
          </div>
        </CardContent>
      </Card>
    </main>
  );
}
