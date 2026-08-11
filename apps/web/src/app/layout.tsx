import type { ReactNode } from 'react';
import './globals.css';
import { AuthProvider } from '../lib/auth-context';

export const metadata = {
  title: 'CapabilityOS Learner Platform',
  description: 'Practical industry-experience platform for learners',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-100 antialiased min-h-screen">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
