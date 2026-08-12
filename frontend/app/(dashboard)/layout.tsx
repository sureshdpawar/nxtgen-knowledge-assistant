"use client";

import { ReactNode, useEffect } from "react";
import { useRouter } from "next/navigation";

import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";

import { useAuth } from "@/hooks/useAuth";

type Props = {
  children: ReactNode;
};

export default function DashboardLayout({
  children,
}: Props) {
  const router = useRouter();

  const {
    authenticated,
    loading,
  } = useAuth();

  useEffect(() => {
    if (!loading && !authenticated) {
      router.replace("/login");
    }
  }, [
    loading,
    authenticated,
    router,
  ]);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        Loading...
      </div>
    );
  }

  if (!authenticated) {
    return null;
  }

  return (
    <div className="flex h-screen flex-col">
      <Header />

      <div className="flex flex-1 overflow-hidden">
        <Sidebar />

        <main className="flex-1 overflow-auto bg-slate-100 p-6">
          {children}
        </main>
      </div>
    </div>
  );
}