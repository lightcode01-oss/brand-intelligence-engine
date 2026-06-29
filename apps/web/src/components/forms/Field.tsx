import React from 'react';
import { cn } from '@/lib/utils/cn';

interface FieldProps {
  label?: string;
  error?: string;
  className?: string;
  children: React.ReactNode;
}

export function Field({ label, error, className, children }: FieldProps) {
  return (
    <div className={cn('flex flex-col gap-1.5', className)}>
      {label && (
        <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
          {label}
        </label>
      )}
      {children}
      {error && (
        <span className="text-xs font-medium text-red-500 dark:text-red-400">
          {error}
        </span>
      )}
    </div>
  );
}
