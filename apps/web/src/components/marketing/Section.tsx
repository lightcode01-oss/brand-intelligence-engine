import React from 'react';
import { cn } from '@/lib/utils/cn';

interface SectionProps extends React.HTMLAttributes<HTMLElement> {
  as?: React.ElementType;
  container?: boolean;
  narrow?: boolean;
  id?: string;
}

/**
 * Reusable section wrapper with consistent vertical padding and optional container.
 */
export function Section({
  as: Tag = 'section',
  container = true,
  narrow = false,
  className,
  children,
  ...props
}: SectionProps) {
  return (
    <Tag className={cn('py-20 lg:py-28', className)} {...props}>
      {container ? (
        <div className={cn('mx-auto px-6', narrow ? 'max-w-3xl' : 'max-w-7xl')}>
          {children}
        </div>
      ) : (
        children
      )}
    </Tag>
  );
}

interface SectionHeadingProps {
  eyebrow?: string;
  title: string;
  description?: string;
  align?: 'left' | 'center';
  className?: string;
}

export function SectionHeading({
  eyebrow,
  title,
  description,
  align = 'center',
  className,
}: SectionHeadingProps) {
  return (
    <div
      className={cn(
        'mb-14',
        align === 'center' ? 'text-center' : 'text-left',
        className
      )}
    >
      {eyebrow && (
        <p className="mb-3 text-sm font-semibold uppercase tracking-widest text-indigo-600">
          {eyebrow}
        </p>
      )}
      <h2 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl lg:text-5xl">
        {title}
      </h2>
      {description && (
        <p
          className={cn(
            'mt-5 text-lg text-slate-600',
            align === 'center' ? 'mx-auto max-w-2xl' : ''
          )}
        >
          {description}
        </p>
      )}
    </div>
  );
}
