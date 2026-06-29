'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Receipt, CheckCircle, Clock, XCircle } from 'lucide-react';

interface Invoice {
  id: string;
  amount: number;
  currency: string;
  status: 'PAID' | 'OPEN' | 'VOID';
  billing_reason: string;
  created_at: string;
}

function InvoiceStatusBadge({ status }: { status: Invoice['status'] }) {
  const config = {
    PAID: {
      label: 'Paid',
      icon: CheckCircle,
      className: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    },
    OPEN: {
      label: 'Open',
      icon: Clock,
      className: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    },
    VOID: {
      label: 'Void',
      icon: XCircle,
      className: 'bg-red-500/10 text-red-400 border-red-500/20',
    },
  };
  const { label, icon: Icon, className } = config[status] ?? config.OPEN;
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium ${className}`}
    >
      <Icon size={11} />
      {label}
    </span>
  );
}

function formatAmount(amount: number, currency: string) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency || 'USD',
  }).format(amount);
}

function formatDate(iso: string) {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(new Date(iso));
}

export default function InvoicesPage() {
  const { data: invoicesResponse, isLoading, error } = useQuery({
    queryKey: ['billing-invoices'],
    queryFn: () => apiClient.get('/billing/invoices?limit=50').then((res) => res.data),
  });

  const invoices: Invoice[] = invoicesResponse?.data ?? [];
  const totalPaid = invoices
    .filter((inv) => inv.status === 'PAID')
    .reduce((sum, inv) => sum + inv.amount, 0);

  return (
    <div className="space-y-8">
      {/* Page header */}
      <div>
        <h1 className="text-3xl font-bold text-white tracking-tight">Invoice History</h1>
        <p className="text-muted mt-1">Review and download your billing statements.</p>
      </div>

      {/* Summary strip */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/10">
                <CheckCircle size={20} className="text-emerald-400" />
              </div>
              <div>
                <p className="text-xs text-muted uppercase tracking-wide">Total Paid</p>
                <p className="text-xl font-bold text-white">{formatAmount(totalPaid, 'USD')}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-violet-500/10">
                <Receipt size={20} className="text-violet-400" />
              </div>
              <div>
                <p className="text-xs text-muted uppercase tracking-wide">Total Invoices</p>
                <p className="text-xl font-bold text-white">{invoices.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/10">
                <Clock size={20} className="text-amber-400" />
              </div>
              <div>
                <p className="text-xs text-muted uppercase tracking-wide">Open Invoices</p>
                <p className="text-xl font-bold text-white">
                  {invoices.filter((i) => i.status === 'OPEN').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Invoice table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Receipt size={18} className="text-violet-400" />
            Billing Statements
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-14 animate-pulse rounded-xl bg-white/5" />
              ))}
            </div>
          ) : error ? (
            <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-6 text-center">
              <p className="text-sm text-red-400">Failed to load invoices. Please try again.</p>
            </div>
          ) : invoices.length === 0 ? (
            <div className="rounded-xl border border-white/5 bg-white/5 p-12 text-center">
              <Receipt size={40} className="mx-auto mb-3 text-muted opacity-40" />
              <p className="text-sm text-muted">No invoices yet.</p>
              <p className="mt-1 text-xs text-muted opacity-60">
                Invoices will appear here after your first payment.
              </p>
            </div>
          ) : (
            <div className="overflow-hidden rounded-xl border border-white/5">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/5 bg-white/5">
                    <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wide">
                      Invoice
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wide">
                      Date
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wide">
                      Description
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-muted uppercase tracking-wide">
                      Amount
                    </th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-muted uppercase tracking-wide">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {invoices.map((invoice) => (
                    <tr
                      key={invoice.id}
                      className="transition-colors hover:bg-white/5"
                    >
                      <td className="px-4 py-4 font-mono text-xs text-muted">
                        #{invoice.id.slice(0, 8).toUpperCase()}
                      </td>
                      <td className="px-4 py-4 text-white">{formatDate(invoice.created_at)}</td>
                      <td className="max-w-xs truncate px-4 py-4 text-muted">
                        {invoice.billing_reason}
                      </td>
                      <td className="px-4 py-4 text-right font-semibold text-white">
                        {formatAmount(invoice.amount, invoice.currency)}
                      </td>
                      <td className="px-4 py-4 text-center">
                        <InvoiceStatusBadge status={invoice.status} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
