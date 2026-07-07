import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";
import { ReactNode } from "react";

export const metadata: Metadata = {
  title: "Affiliate Booking Admin",
  description: "Standalone admin UI for managing creator profiles."
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen">
          <header className="border-b border-slate-200 bg-white">
            <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
              <Link href="/" className="text-lg font-semibold text-slate-900">Affiliate Booking Admin</Link>
              <nav className="flex gap-4 text-sm text-slate-600">
                <Link href="/register">Register</Link>
                <Link href="/login">Login</Link>
                <Link href="/dashboard">Dashboard</Link>
                <Link href="/edit-profile">Edit Profile</Link>
              </nav>
            </div>
          </header>
          <main>{children}</main>
        </div>
      </body>
    </html>
  );
}
