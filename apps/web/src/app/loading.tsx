import React from 'react';

export default function Loading() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 dark:bg-slate-900 transition-colors duration-300">
      <div className="flex flex-col items-center gap-4">
        {/* Loading Spinner */}
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-indigo-600 dark:border-slate-800" />
        <span className="text-sm font-medium text-slate-500 dark:text-slate-400">Loading Nomen...</span>
      </div>
    </div>
  );
}
