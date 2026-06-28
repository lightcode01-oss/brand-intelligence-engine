import type { Metadata } from 'next';
import './globals.css';

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
      <body>{children}</body>
    </html>
  );
}
