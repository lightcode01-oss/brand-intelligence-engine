'use client';

import React, { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Unhandled app error occurred:', error);
  }, [error]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-50 px-6 py-12 dark:bg-slate-900">
      <div className="text-center">
        <div className="mx-auto mb-4 h-12 w-12 rounded-xl bg-red-100 p-2 text-red-600 dark:bg-red-950/30">
          <svg fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="h-8 w-8">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
          </svg>
        </div>
        <h2 className="mb-2 font-semibold text-2xl tracking-tight text-slate-900 dark:text-white">Something went wrong!</h2>
        <p className="mb-6 text-sm text-slate-500 dark:text-slate-400">An unexpected system error has occurred. Our engineers are tracking this.</p>
        <button
          onClick={() => reset()}
          className="rounded-lg bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 transition-all"
        >
          Try Again
        </button>
      </div>
    </div>
  );
}
