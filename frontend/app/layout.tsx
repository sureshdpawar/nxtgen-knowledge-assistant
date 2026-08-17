import type {
  Metadata,
} from "next";

import {
  Geist,
  Geist_Mono,
} from "next/font/google";

import type {
  ReactNode,
} from "react";

import {
  AuthProvider,
} from "@/providers/AuthProvider";

import QueryProvider from "@/providers/QueryProvider";

import "./globals.css";


const geistSans = Geist({
  variable:
    "--font-geist-sans",

  subsets: [
    "latin",
  ],
});


const geistMono = Geist_Mono({
  variable:
    "--font-geist-mono",

  subsets: [
    "latin",
  ],
});


export const metadata:
  Metadata = {
    title:
      "NXTGEN Knowledge Assistant",

    description:
      "AI Knowledge Platform",
  };


export default function RootLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable}`}
    >
      <body
        suppressHydrationWarning
        className="min-h-screen bg-slate-100 antialiased"
      >
        <QueryProvider>

          <AuthProvider>
            {children}
          </AuthProvider>

        </QueryProvider>
      </body>
    </html>
  );
}