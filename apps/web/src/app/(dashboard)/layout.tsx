'use client';

import React, { useEffect, useState } from 'react';
import { useSidebarStore } from '@/store/sidebarStore';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { useWebSocketStore } from '@/store/websocketStore';
import { apiClient } from '@/lib/api/client';
import { 
  Menu, Bell, User, LayoutDashboard, Settings, Layers, Key,
  Heart, Folder, Activity, Search, Circle
} from 'lucide-react';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const sidebar = useSidebarStore();
  const workspace = useWorkspaceStore();
  const wsStore = useWebSocketStore();
  const [unreadCount, setUnreadCount] = useState(0);

  // 1. WebSocket connection hook
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const token = localStorage.getItem('access_token');
    const wsId = workspace.activeWorkspace?.id;
    
    if (token && wsId) {
      wsStore.connect(token, wsId);
    }
    
    return () => {
      wsStore.disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [workspace.activeWorkspace?.id]);

  // 2. Fetch initial unread count and listen for notifications updates
  useEffect(() => {
    const fetchUnread = async () => {
      try {
        const res = await apiClient.get('/notifications/unread-count');
        setUnreadCount(res.data?.data?.unread_count || 0);
      } catch (err) {
        console.error('Failed to fetch unread notification count:', err);
      }
    };
    fetchUnread();

    const handleNotification = () => {
      setUnreadCount((c) => c + 1);
    };

    if (typeof window !== 'undefined') {
      window.addEventListener('ws:notification_received', handleNotification);
    }
    return () => {
      if (typeof window !== 'undefined') {
        window.removeEventListener('ws:notification_received', handleNotification);
      }
    };
  }, [workspace.activeWorkspace?.id]);

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50 dark:bg-slate-900 transition-colors duration-300">
      {/* Sidebar Drawer */}
      <aside className={`flex flex-col border-r border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950 transition-all duration-300 ${sidebar.isOpen ? 'w-64' : 'w-20'}`}>
        <div className="flex h-16 items-center gap-2 px-6">
          <div className="h-8 w-8 min-w-8 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white">N</div>
          {sidebar.isOpen && <span className="font-semibold text-lg dark:text-white">Nomen</span>}
        </div>
        
        {/* Navigation Items */}
        <nav className="flex-1 space-y-1 px-4 py-4 overflow-y-auto">
          <a href="/dashboard" className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-900">
            <LayoutDashboard className="h-5 w-5 min-w-5 text-indigo-600" />
            {sidebar.isOpen && <span>Dashboard</span>}
          </a>
          <a href="/projects" className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-900">
            <Layers className="h-5 w-5 min-w-5" />
            {sidebar.isOpen && <span>Projects</span>}
          </a>
          <a href="/favorites" className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-900">
            <Heart className="h-5 w-5 min-w-5 text-red-500" />
            {sidebar.isOpen && <span>Favorites</span>}
          </a>
          <a href="/collections" className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-900">
            <Folder className="h-5 w-5 min-w-5 text-amber-500" />
            {sidebar.isOpen && <span>Collections</span>}
          </a>
          <a href="/activity" className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-900">
            <Activity className="h-5 w-5 min-w-5 text-emerald-500" />
            {sidebar.isOpen && <span>Activity Feed</span>}
          </a>
          <a href="/search" className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-900">
            <Search className="h-5 w-5 min-w-5" />
            {sidebar.isOpen && <span>Search</span>}
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
            
            {/* Real-time Workspace Presence Indicators */}
            {wsStore.status === 'connected' && (
              <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/20 text-xxs font-medium text-emerald-700 dark:text-emerald-400">
                <Circle className="h-2 w-2 fill-emerald-500 text-emerald-500 animate-pulse" />
                <span>{wsStore.activeUsers.length} Online</span>
              </div>
            )}
          </div>
          
          <div className="flex items-center gap-4">
            <a 
              href="/notifications" 
              className="relative rounded-lg p-1.5 hover:bg-slate-100 dark:hover:bg-slate-900 text-slate-600 dark:text-slate-400"
            >
              <Bell className="h-5 w-5" />
              {unreadCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
                  {unreadCount}
                </span>
              )}
            </a>
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
