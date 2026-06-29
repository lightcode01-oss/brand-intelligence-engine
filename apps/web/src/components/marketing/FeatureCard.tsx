import React from 'react';
import { cn } from '@/lib/utils/cn';
import { LucideIcon } from 'lucide-react';

interface FeatureCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
  className?: string;
  accent?: 'indigo' | 'violet' | 'cyan' | 'emerald' | 'amber' | 'rose';
}

const ACCENT_CLASSES = {
  indigo: {
    bg: 'bg-indigo-50',
    icon: 'bg-indigo-100 text-indigo-700',
    border: 'group-hover:border-indigo-300',
  },
  violet: {
    bg: 'bg-violet-50',
    icon: 'bg-violet-100 text-violet-700',
    border: 'group-hover:border-violet-300',
  },
  cyan: {
    bg: 'bg-cyan-50',
    icon: 'bg-cyan-100 text-cyan-700',
    border: 'group-hover:border-cyan-300',
  },
  emerald: {
    bg: 'bg-emerald-50',
    icon: 'bg-emerald-100 text-emerald-700',
    border: 'group-hover:border-emerald-300',
  },
  amber: {
    bg: 'bg-amber-50',
    icon: 'bg-amber-100 text-amber-700',
    border: 'group-hover:border-amber-300',
  },
  rose: {
    bg: 'bg-rose-50',
    icon: 'bg-rose-100 text-rose-700',
    border: 'group-hover:border-rose-300',
  },
};

export function FeatureCard({
  icon: Icon,
  title,
  description,
  className,
  accent = 'indigo',
}: FeatureCardProps) {
  const styles = ACCENT_CLASSES[accent];
  return (
    <div
      className={cn(
        'group rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all hover:-translate-y-1 hover:shadow-md',
        styles.border,
        className
      )}
    >
      <div
        className={cn(
          'mb-4 flex h-11 w-11 items-center justify-center rounded-xl',
          styles.icon
        )}
        aria-hidden="true"
      >
        <Icon size={22} strokeWidth={1.75} />
      </div>
      <h3 className="mb-2 text-base font-semibold text-slate-900">{title}</h3>
      <p className="text-sm leading-relaxed text-slate-500">{description}</p>
    </div>
  );
}
