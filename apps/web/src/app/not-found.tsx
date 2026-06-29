import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-50 px-6 py-12 dark:bg-slate-900">
      <div className="text-center">
        <h1 className="mb-2 font-bold text-6xl text-indigo-600">404</h1>
        <h2 className="mb-2 font-semibold text-2xl tracking-tight text-slate-900 dark:text-white">Page Not Found</h2>
        <p className="mb-6 text-sm text-slate-500 dark:text-slate-400">Sorry, we could not find the page you are looking for.</p>
        <Link
          href="/"
          className="rounded-lg bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 transition-all"
        >
          Go Back Home
        </Link>
      </div>
    </div>
  );
}
