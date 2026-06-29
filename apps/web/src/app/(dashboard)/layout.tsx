'use client';

import React from 'react';
import { useSidebarStore } from '@/store/sidebarStore';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { Menu, Bell, User, LayoutDashboard, Settings, Layers, Key } from 'lucide-react';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const sidebar = useSidebarStore();
  const workspace = useWorkspaceStore();

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50 dark:bg-slate-900 transition-colors duration-300">
      {/* Sidebar Drawer */}
      <aside className={`flex flex-col border-r border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950 transition-all duration-300 ${sidebar.isOpen ? 'w-64' : 'w-20'}`}>
        <div className="flex h-16 items-center gap-2 px-6">
          <div className="h-8 w-8 min-w-8 rounded-lg bg-indigo-600" />
          {sidebar.isOpen && <span className="font-semibold text-lg dark:text-white">Nomen</span>}
        </div>
        
        {/* Navigation Items */}
        <nav className="flex-1 space-y-1 px-4 py-4">
          <a href="/dashboard" className="flex items-center gap-3 rounded-lg bg-slate-100 px-3 py-2 text-sm font-medium text-slate-900 dark:bg-slate-900 dark:text-white">
            <LayoutDashboard className="h-5 w-5 min-w-5 text-indigo-600" />
            {sidebar.isOpen && <span>Dashboard</span>}
          </a>
          <a href="/projects" className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-900">
            <Layers className="h-5 w-5 min-w-5" />
            {sidebar.isOpen && <span>Projects</span>}
          </a>
          <a href="/keys" className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-900">
            <Key className="h-5 w-5 min-w-5" />
            {sidebar.isOpen && <span>API Keys</span>}
          </a>
          <a href="/settings" className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-900">
            <Settings className="h-5 w-5 min-w-5" />
            {sidebar.isOpen && <span>Settings</span>}
          </a>
        </nav>
      </aside>

      {/* Main Panel */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Dashboard Header */}
        <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-6 dark:border-slate-800 dark:bg-slate-950">
          <div className="flex items-center gap-4">
            <button onClick={sidebar.toggle} className="rounded-lg p-1.5 hover:bg-slate-100 dark:hover:bg-slate-900 text-slate-600 dark:text-slate-400">
              <Menu className="h-5 w-5" />
            </button>
            <div className="hidden sm:block text-sm text-slate-500 dark:text-slate-400">
              Active Workspace: <span className="font-semibold text-slate-800 dark:text-slate-200">{workspace.activeWorkspace?.name || 'Personal'}</span>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <button className="relative rounded-lg p-1.5 hover:bg-slate-100 dark:hover:bg-slate-900 text-slate-600 dark:text-slate-400">
              <Bell className="h-5 w-5" />
            </button>
            <button className="rounded-lg p-1.5 hover:bg-slate-100 dark:hover:bg-slate-900 text-slate-600 dark:text-slate-400">
              <User className="h-5 w-5" />
            </button>
          </div>
        </header>

        {/* Dashboard Panels Scroll */}
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  );
}
