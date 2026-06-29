import type { Metadata } from 'next';
import './globals.css';
import ThemeProvider from '@/components/providers/ThemeProvider';
import QueryProvider from '@/components/providers/QueryProvider';
import AnalyticsProvider from '@/components/analytics/AnalyticsProvider';

export const metadata: Metadata = {
  title: 'Nomen - Brand Intelligence Platform',
  description: 'AI-Powered Brand Discovery and Legal Clearance Engine',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <QueryProvider>
          <ThemeProvider>
            <AnalyticsProvider>
              {children}
            </AnalyticsProvider>
          </ThemeProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
