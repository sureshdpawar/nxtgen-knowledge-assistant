"use client";

import {
  ReactNode,
  useEffect,
  useState,
} from "react";

import {
  usePathname,
  useRouter,
} from "next/navigation";

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
  const pathname = usePathname();

  const {
    authenticated,
    loading,
  } = useAuth();

  const [
    mobileSidebarOpen,
    setMobileSidebarOpen,
  ] = useState(false);

  useEffect(() => {
    if (
      !loading &&
      !authenticated
    ) {
      router.replace("/login");
    }
  }, [
    loading,
    authenticated,
    router,
  ]);

  useEffect(() => {
    setMobileSidebarOpen(false);
  }, [pathname]);

  useEffect(() => {
    if (!mobileSidebarOpen) {
      return;
    }

    const previousOverflow =
      document.body.style.overflow;

    document.body.style.overflow =
      "hidden";

    return () => {
      document.body.style.overflow =
        previousOverflow;
    };
  }, [mobileSidebarOpen]);

  useEffect(() => {
    if (!mobileSidebarOpen) {
      return;
    }

    function handleKeyDown(
      event: KeyboardEvent,
    ) {
      if (event.key === "Escape") {
        setMobileSidebarOpen(false);
      }
    }

    window.addEventListener(
      "keydown",
      handleKeyDown,
    );

    return () => {
      window.removeEventListener(
        "keydown",
        handleKeyDown,
      );
    };
  }, [mobileSidebarOpen]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-100">
        <div className="text-sm font-medium text-slate-600">
          Loading...
        </div>
      </div>
    );
  }

  if (!authenticated) {
    return null;
  }

  return (
    <div className="flex h-dvh min-h-screen flex-col overflow-hidden bg-slate-100">

      <Header
        onMenuClick={() =>
          setMobileSidebarOpen(true)
        }
      />

      <div className="relative flex min-h-0 flex-1">

        <div className="dashboard-desktop-sidebar shrink-0">
          <Sidebar />
        </div>

        <main
          className="
            min-w-0
            flex-1
            overflow-x-hidden
            overflow-y-auto
            bg-slate-100
          "
        >
          <div
            className="
              mx-auto
              w-full
              p-4
              sm:p-5
              md:p-6
            "
          >
            {children}
          </div>
        </main>

        {mobileSidebarOpen && (
          <div
            className="
              dashboard-mobile-sidebar
              fixed
              inset-0
              z-50
            "
            role="dialog"
            aria-modal="true"
            aria-label="Navigation menu"
          >

            <button
              type="button"
              aria-label="Close navigation menu"
              onClick={() =>
                setMobileSidebarOpen(false)
              }
              className="
                absolute
                inset-0
                bg-slate-950/40
                backdrop-blur-[1px]
              "
            />

            <div
              className="
                absolute
                inset-y-0
                left-0
                flex
                w-[min(18rem,85vw)]
                max-w-full
                flex-col
                bg-white
                shadow-2xl
              "
            >
              <Sidebar
                mobile
                onNavigate={() =>
                  setMobileSidebarOpen(false)
                }
                onClose={() =>
                  setMobileSidebarOpen(false)
                }
              />
            </div>

          </div>
        )}

      </div>

    </div>
  );
}