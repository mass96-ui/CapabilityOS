import type { ReactNode } from 'react';
import './globals.css';

export const metadata = {
  title: 'CapabilityOS Admin',
  description: 'CapabilityOS admin foundation',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
