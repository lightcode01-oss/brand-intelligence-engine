import React from 'react';

export default function MarketingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen flex-col bg-slate-50 text-slate-900 transition-colors duration-300">
      {/* Sticky Marketing Header */}
      <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/80 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-indigo-600" />
            <span className="font-semibold text-lg tracking-tight">Nomen</span>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-600">
            <a href="#features" className="hover:text-indigo-600">Features</a>
            <a href="#pricing" className="hover:text-indigo-600">Pricing</a>
            <a href="#about" className="hover:text-indigo-600">About</a>
          </nav>
          <div className="flex items-center gap-4">
            <a href="/auth/login" className="text-sm font-medium hover:text-indigo-600">Sign In</a>
            <a href="/auth/register" className="rounded-lg bg-indigo-600 px-4 h-9 flex items-center text-sm font-medium text-white hover:bg-indigo-700 transition-all shadow-sm">
              Get Started
            </a>
          </div>
        </div>
      </header>
      
      {/* Main Content Area */}
      <main className="flex-1">{children}</main>
      
      {/* Marketing Footer */}
      <footer className="border-t border-slate-200 bg-white py-8">
        <div className="mx-auto max-w-7xl px-6 text-center text-sm text-slate-500">
          <p>&copy; {new Date().getFullYear()} Nomen. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
