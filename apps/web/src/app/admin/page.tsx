'use client';

import React, { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Loader2, ShieldCheck, ShieldAlert, Cpu, Users, Eye, RefreshCw, ToggleLeft, ToggleRight } from 'lucide-react';

interface UserItem {
  id: string;
  email: string;
  role: string;
  status: string;
}

interface ProviderMetric {
  requests_total: number;
  latency_avg_ms: number;
  cost_estimate_usd: number;
  success_rate: number;
  failure_rate: number;
  requests_per_minute: number;
}

interface AuditLogEntry {
  id: string;
  actor: string;
  action: string;
  entity_name: string;
  entity_id: string | null;
  ip_address: string | null;
  user_agent: string | null;
  request_id: string | null;
  created_at: string;
}

export default function AdminDashboard() {
  const [loading, setLoading] = useState(true);
  const [users, setUsers] = useState<UserItem[]>([]);
  const [providers, setProviders] = useState<Record<string, ProviderMetric>>({});
  const [maintenance, setMaintenance] = useState(false);
  const [auditLogs, setAuditLogs] = useState<AuditLogEntry[]>([]);
  const [searchLogAction, setSearchLogAction] = useState('');
  const [updatingUser, setUpdatingUser] = useState<string | null>(null);

  const fetchAdminData = async () => {
    setLoading(true);
    try {
      // 1. Fetch Users
      const usersRes = await apiClient.get('/admin/users');
      setUsers(usersRes.data?.data || []);

      // 2. Fetch Providers Telemetry
      const provRes = await apiClient.get('/admin/providers');
      setProviders(provRes.data?.data || {});

      // 3. Fetch Audit Logs
      const auditRes = await apiClient.get('/admin/audit-logs');
      setAuditLogs(auditRes.data?.data || []);
      
    } catch (err) {
      console.error('Failed to load administrative panel data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminData();
  }, []);

  const handleToggleMaintenance = async () => {
    try {
      const nextState = !maintenance;
      await apiClient.post(`/admin/maintenance?enabled=${nextState}`);
      setMaintenance(nextState);
      alert(`System maintenance mode set to ${nextState}`);
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpdateRole = async (userId: string, newRole: string) => {
    setUpdatingUser(userId);
    try {
      await apiClient.put(`/admin/users/${userId}?role=${newRole}`);
      setUsers(prev => prev.map(u => u.id === userId ? { ...u, role: newRole } : u));
    } catch (err) {
      console.error(err);
    } finally {
      setUpdatingUser(null);
    }
  };

  const handleUpdateStatus = async (userId: string, newStatus: string) => {
    setUpdatingUser(userId);
    try {
      await apiClient.put(`/admin/users/${userId}?status=${newStatus}`);
      setUsers(prev => prev.map(u => u.id === userId ? { ...u, status: newStatus } : u));
    } catch (err) {
      console.error(err);
    } finally {
      setUpdatingUser(null);
    }
  };

  const handleSearchAudit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await apiClient.get(`/admin/audit-logs?action=${searchLogAction}`);
      setAuditLogs(res.data?.data || []);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-6">
      {/* Top Header */}
      <div className="flex justify-between items-center border-b border-slate-200 dark:border-slate-800 pb-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2">
            <ShieldCheck className="h-8 w-8 text-indigo-600 animate-pulse" /> Nomen Admin Portal
          </h1>
          <p className="text-sm text-slate-500 mt-1">Global platform configs, user roles, celery worker monitoring, and telemetry logs.</p>
        </div>
        <Button variant="outline" size="sm" onClick={fetchAdminData} disabled={loading} className="flex items-center gap-1">
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Sync Dashboard</span>
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-32">
          <Loader2 className="h-12 w-12 animate-spin text-indigo-600" />
        </div>
      ) : (
        <div className="space-y-6">
          {/* Dynamic Settings: Maintenance & Feature Flags */}
          <div className="grid gap-6 md:grid-cols-3">
            <Card className="md:col-span-1 border-red-100 dark:border-red-950/20 bg-red-50/10">
              <CardHeader>
                <CardTitle className="text-sm font-bold flex items-center gap-1 text-red-600">
                  <ShieldAlert className="h-4 w-4" /> Global Maintenance Filter
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-xs text-slate-500">
                  Activating maintenance mode immediately rejects all public client requests with a 503 Service Unavailable envelope.
                </p>
                <button 
                  onClick={handleToggleMaintenance}
                  className="flex items-center gap-2 hover:opacity-85 transition"
                >
                  {maintenance ? (
                    <ToggleRight className="h-8 w-8 text-red-650 text-red-500" />
                  ) : (
                    <ToggleLeft className="h-8 w-8 text-slate-400" />
                  )}
                  <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                    {maintenance ? 'Active (503 Enabled)' : 'Inactive'}
                  </span>
                </button>
              </CardContent>
            </Card>

            {/* AI Providers Telemetry Monitor */}
            <Card className="md:col-span-2">
              <CardHeader>
                <CardTitle className="text-sm font-semibold flex items-center gap-1.5">
                  <Cpu className="h-4 w-4 text-indigo-600" /> AI Provider Latency Monitoring
                </CardTitle>
              </CardHeader>
              <CardContent className="grid gap-4 sm:grid-cols-2">
                {Object.entries(providers).map(([name, data]) => (
                  <div key={name} className="p-4 rounded-xl border border-slate-100 dark:border-slate-800 space-y-2 text-xs">
                    <div className="flex justify-between font-bold border-b border-slate-100 dark:border-slate-850 pb-1 uppercase">
                      <span className="text-slate-850 dark:text-slate-200">{name.split('-')[0]}</span>
                      <span className="text-indigo-600">{data.latency_avg_ms.toFixed(0)} ms</span>
                    </div>
                    <div className="flex justify-between text-slate-500">
                      <span>Requests total</span>
                      <span className="font-bold text-slate-800 dark:text-slate-350">{data.requests_total} queries</span>
                    </div>
                    <div className="flex justify-between text-slate-500">
                      <span>Success rate</span>
                      <span className="font-bold text-emerald-600">{data.success_rate.toFixed(1)}%</span>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* User management list */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-semibold flex items-center gap-1.5">
                <Users className="h-4 w-4 text-indigo-600" /> User Accounts Administration ({users.length})
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0 overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/10 text-slate-550 uppercase font-semibold">
                    <th className="p-4">Email Account</th>
                    <th className="p-4 text-center">User Role</th>
                    <th className="p-4 text-center">User Status</th>
                    <th className="p-4 text-center">Permissions Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {users.map((u) => (
                    <tr key={u.id} className="hover:bg-slate-50/30 dark:hover:bg-slate-900/5">
                      <td className="p-4 font-semibold text-slate-800 dark:text-slate-200">{u.email}</td>
                      <td className="p-4 text-center">
                        <select
                          value={u.role}
                          onChange={(e) => handleUpdateRole(u.id, e.target.value)}
                          disabled={updatingUser === u.id}
                          className="px-2 py-1 rounded border border-slate-250 bg-transparent text-slate-800 dark:border-slate-800 dark:text-white"
                        >
                          <option value="FREE_USER">Free User</option>
                          <option value="PRO_USER">Pro User</option>
                          <option value="ADMIN">Admin</option>
                        </select>
                      </td>
                      <td className="p-4 text-center">
                        <span className={`inline-block px-2.5 py-0.5 rounded text-[10px] font-bold ${u.status === 'ACTIVE' ? 'bg-emerald-50 text-emerald-600 dark:bg-emerald-950/20' : 'bg-red-50 text-red-500 dark:bg-red-950/20'}`}>
                          {u.status}
                        </span>
                      </td>
                      <td className="p-4 text-center">
                        <button
                          onClick={() => handleUpdateStatus(u.id, u.status === 'ACTIVE' ? 'SUSPENDED' : 'ACTIVE')}
                          disabled={updatingUser === u.id}
                          className="px-3 py-1 bg-slate-100 dark:bg-slate-800 hover:opacity-85 text-slate-700 dark:text-slate-200 rounded font-semibold text-xxs"
                        >
                          Toggle Active
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>

          {/* Audit Logs Search timeline */}
          <Card>
            <CardHeader className="flex flex-row justify-between items-center border-b border-slate-100 dark:border-slate-800 pb-3">
              <CardTitle className="text-sm font-semibold flex items-center gap-1.5">
                <Eye className="h-4 w-4 text-indigo-600" /> Platform Security Audit Trail Logs
              </CardTitle>
              <form onSubmit={handleSearchAudit} className="flex gap-2">
                <Input 
                  placeholder="Filter action (USER_LOGIN_SUCCESS)..."
                  value={searchLogAction}
                  onChange={(e) => setSearchLogAction(e.target.value)}
                  className="h-8 max-w-xs text-xs"
                />
                <Button type="submit" size="sm" className="h-8">Search</Button>
              </form>
            </CardHeader>
            <CardContent className="p-0 max-h-[300px] overflow-y-auto">
              <table className="w-full text-left border-collapse text-xxs">
                <thead>
                  <tr className="border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/10 text-slate-500 uppercase font-semibold">
                    <th className="p-3">Timestamp</th>
                    <th className="p-3">Actor</th>
                    <th className="p-3">Action</th>
                    <th className="p-3">Target Entity</th>
                    <th className="p-3">IP Address</th>
                    <th className="p-3">Trace Request ID</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800 text-slate-650 dark:text-slate-400">
                  {auditLogs.map((l) => (
                    <tr key={l.id} className="hover:bg-slate-50/30 dark:hover:bg-slate-900/5">
                      <td className="p-3 whitespace-nowrap">{new Date(l.created_at).toLocaleString()}</td>
                      <td className="p-3 font-semibold">{l.actor}</td>
                      <td className="p-3 text-indigo-600 font-semibold">{l.action}</td>
                      <td className="p-3 capitalize">{l.entity_name}</td>
                      <td className="p-3">{l.ip_address || '127.0.0.1'}</td>
                      <td className="p-3 font-mono">{l.request_id || 'system'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
