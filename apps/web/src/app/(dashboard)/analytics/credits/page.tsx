'use client';

import React, { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Loader2, DollarSign, ArrowUpRight, ArrowDownLeft, Calendar } from 'lucide-react';

interface Transaction {
  id: string;
  amount: number;
  type: string;
  created_at: string;
}

export default function CreditsAnalytics() {
  const [loading, setLoading] = useState(true);
  const [balance, setBalance] = useState(0);
  const [credited, setCredited] = useState(0);
  const [debited, setDebited] = useState(0);
  const [txns, setTxns] = useState<Transaction[]>([]);

  useEffect(() => {
    const fetchCredits = async () => {
      try {
        const res = await apiClient.get('/analytics/credits');
        const data = res.data?.data;
        if (data) {
          setBalance(data.current_balance);
          setCredited(data.total_credited);
          setDebited(data.total_debited);
          setTxns(data.transactions || []);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchCredits();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Credits & Transactions Balance</h1>
        <p className="text-sm text-slate-500 mt-1">Audit trail log of dynamic debits, refunds, and subscriptions credits additions.</p>
      </div>

      <div className="flex gap-1 border-b border-slate-200 dark:border-slate-800 pb-px">
        <a href="/analytics" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Overview</a>
        <a href="/analytics/credits" className="px-4 py-2 border-b-2 border-indigo-600 text-indigo-600 dark:text-indigo-400 font-semibold text-sm">Credits Balance</a>
        <a href="/analytics/usage" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Usage Logs</a>
        <a href="/analytics/team" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Team Activity</a>
        <a href="/analytics/workspace" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Workspace Growth</a>
        <a href="/analytics/ai" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">AI Performance</a>
        <a href="/analytics/trends" className="px-4 py-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-medium text-sm">Score Trends</a>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-20">
          <Loader2 className="h-10 w-10 animate-spin text-indigo-600" />
        </div>
      ) : (
        <div className="space-y-6">
          {/* Top Info Cards */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card className="bg-indigo-600 text-white border-none shadow-lg">
              <CardContent className="pt-6">
                <span className="text-xs text-indigo-200 font-semibold uppercase">Remaining Credits Balance</span>
                <p className="text-3xl font-bold mt-1 flex items-center gap-1">
                  <DollarSign className="h-7 w-7" /> {balance.toFixed(1)}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6 flex justify-between items-center">
                <div>
                  <span className="text-xs text-slate-500 font-semibold uppercase">Total Purchased / Credited</span>
                  <p className="text-2xl font-bold mt-1 text-slate-900 dark:text-white">+{credited.toFixed(1)}</p>
                </div>
                <div className="p-2 rounded bg-emerald-50 text-emerald-600 dark:bg-emerald-950/20">
                  <ArrowUpRight className="h-5 w-5" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6 flex justify-between items-center">
                <div>
                  <span className="text-xs text-slate-500 font-semibold uppercase">Total Expended / Debited</span>
                  <p className="text-2xl font-bold mt-1 text-slate-900 dark:text-white">-{debited.toFixed(1)}</p>
                </div>
                <div className="p-2 rounded bg-red-50 text-red-600 dark:bg-red-950/20">
                  <ArrowDownLeft className="h-5 w-5" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Transactions List */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-semibold">Historical Credits Transactions</CardTitle>
            </CardHeader>
            <CardContent className="p-0 divide-y divide-slate-100 dark:divide-slate-800">
              {txns.length === 0 ? (
                <div className="text-center py-10 text-slate-400">No transactions recorded.</div>
              ) : (
                txns.map((t) => (
                  <div key={t.id} className="flex justify-between items-center p-4">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-full ${t.amount < 0 ? 'bg-red-50 text-red-600 dark:bg-red-950/20' : 'bg-emerald-50 text-emerald-600 dark:bg-emerald-950/20'}`}>
                        {t.amount < 0 ? <ArrowDownLeft className="h-4 w-4" /> : <ArrowUpRight className="h-4 w-4" />}
                      </div>
                      <div>
                        <p className="font-semibold text-sm text-slate-900 dark:text-white capitalize">{t.type} transaction</p>
                        <span className="text-xxs text-slate-450 flex items-center gap-1 mt-0.5"><Calendar className="h-3 w-3" /> {new Date(t.created_at).toLocaleString()}</span>
                      </div>
                    </div>
                    <span className={`font-bold text-sm ${t.amount < 0 ? 'text-red-500' : 'text-emerald-500'}`}>
                      {t.amount < 0 ? '' : '+'}{t.amount.toFixed(1)}
                    </span>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
