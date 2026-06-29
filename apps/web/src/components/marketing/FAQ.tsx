'use client';

import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils/cn';

interface FAQItem {
  question: string;
  answer: string;
}

interface FAQProps {
  items: FAQItem[];
}

function FAQRow({ item, index }: { item: FAQItem; index: number }) {
  const [open, setOpen] = useState(false);
  const id = `faq-${index}`;

  return (
    <div className="border-b border-slate-200 last:border-0">
      <button
        id={`${id}-trigger`}
        aria-expanded={open}
        aria-controls={`${id}-content`}
        className="flex w-full items-center justify-between py-5 text-left transition-colors hover:text-indigo-600"
        onClick={() => setOpen(!open)}
      >
        <span className="pr-4 text-base font-medium text-slate-900">{item.question}</span>
        <ChevronDown
          size={18}
          className={cn(
            'flex-shrink-0 text-slate-400 transition-transform duration-200',
            open && 'rotate-180'
          )}
          aria-hidden="true"
        />
      </button>
      <div
        id={`${id}-content`}
        role="region"
        aria-labelledby={`${id}-trigger`}
        hidden={!open}
        className={cn(
          'overflow-hidden transition-all duration-300',
          open ? 'max-h-96 pb-5' : 'max-h-0'
        )}
      >
        <p className="text-sm leading-relaxed text-slate-600">{item.answer}</p>
      </div>
    </div>
  );
}

export function FAQ({ items }: FAQProps) {
  return (
    <div className="divide-y-0" role="list" aria-label="Frequently asked questions">
      {items.map((item, idx) => (
        <FAQRow key={idx} item={item} index={idx} />
      ))}
    </div>
  );
}
