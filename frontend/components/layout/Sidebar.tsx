"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import {
  Bot,
  Building2,
  BrainCircuit,
  Cable,
  ClipboardCheck,
  Database,
  Gauge,
  LayoutDashboard,
  MessageSquare,
  Search,
  Users,
  Wrench,
} from "lucide-react";

import {
  useAuth,
} from "@/hooks/useAuth";

import type {
  UserRole,
} from "@/types/auth";


type MenuItem = {
  label: string;

  href: string;

  icon:
    React.ComponentType<{
      className?: string;
    }>;

  roles: UserRole[];

  section:
    | "main"
    | "knowledge"
    | "studio"
    | "administration";
};


const menu: MenuItem[] = [
  {
    label: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
    roles: [
      "SUPERADMIN",
      "ADMIN",
    ],
    section: "main",
  },

  {
    label: "Knowledge Bases",
    href: "/knowledge-bases",
    icon: Database,
    roles: [
      "ADMIN",
    ],
    section: "knowledge",
  },

  {
    label: "Evaluation",
    href: "/evaluation",
    icon: ClipboardCheck,
    roles: [
      "ADMIN",
    ],
    section: "knowledge",
  },

  {
    label: "Search",
    href: "/search",
    icon: Search,
    roles: [
      "ADMIN",
      "USER",
    ],
    section: "knowledge",
  },

  {
    label: "Chat",
    href: "/chat",
    icon: MessageSquare,
    roles: [
      "ADMIN",
      "USER",
    ],
    section: "knowledge",
  },

  {
    label: "Agents",
    href: "/agents",
    icon: Bot,
    roles: [
      "ADMIN",
    ],
    section: "studio",
  },

  {
    label: "Integrations",
    href: "/integrations",
    icon: Cable,
    roles: [
      "ADMIN",
    ],
    section: "studio",
  },

  {
    label: "Tools",
    href: "/tools",
    icon: Wrench,
    roles: [
      "ADMIN",
    ],
    section: "studio",
  },

  {
    label: "Tenants",
    href: "/tenants",
    icon: Building2,
    roles: [
      "SUPERADMIN",
    ],
    section:
      "administration",
  },

  {
    label: "Users",
    href: "/users",
    icon: Users,
    roles: [
      "ADMIN",
    ],
    section:
      "administration",
  },

  {
    label: "Usage & Limits",
    href: "/usage",
    icon: Gauge,
    roles: [
      "ADMIN",
    ],
    section:
      "administration",
  },

  {
    label: "LLM Profiles",
    href: "/settings",
    icon: BrainCircuit,
    roles: [
      "ADMIN",
    ],
    section:
      "administration",
  },
];


const sectionLabels = {
  main: "",
  knowledge:
    "Knowledge",
  studio:
    "Agent Studio",
  administration:
    "Administration",
} as const;


const sectionOrder:
  MenuItem["section"][] = [
    "main",
    "knowledge",
    "studio",
    "administration",
  ];


export default function Sidebar() {
  const pathname =
    usePathname();

  const {
    user,
  } = useAuth();


  if (!user) {
    return null;
  }


  const visibleMenu =
    menu.filter(
      (item) =>
        item.roles.includes(
          user.role,
        ),
    );


  const showTenant =
    (
      user.role === "ADMIN"
      || user.role === "USER"
    )
    && Boolean(
      user.tenant_name,
    );


  function isActive(
    href: string,
  ) {
    return (
      pathname === href
      || pathname.startsWith(
        `${href}/`,
      )
    );
  }


  return (
    <aside className="flex w-64 flex-col border-r bg-white">

      <div className="border-b px-4 py-3">

        <p className="text-[11px] font-medium uppercase tracking-wide text-slate-400">
          Signed in as
        </p>


        <p className="mt-1 truncate text-sm font-semibold text-slate-800">
          {user.first_name}{" "}
          {user.last_name}
        </p>


        <div className="mt-1 flex min-w-0 items-center gap-1.5 text-xs">

          <span className="font-semibold text-slate-600">
            {user.role}
          </span>


          {showTenant && (
            <>
              <span className="text-slate-300">
                ·
              </span>

              <span className="min-w-0 truncate font-medium text-slate-500">
                {user.tenant_name}
              </span>
            </>
          )}

        </div>

      </div>


      <nav className="flex-1 overflow-y-auto p-4">

        <div className="space-y-6">

          {sectionOrder.map(
            (section) => {
              const items =
                visibleMenu.filter(
                  (item) =>
                    item.section
                    === section,
                );


              if (
                items.length === 0
              ) {
                return null;
              }


              return (
                <div
                  key={
                    section
                  }
                >

                  {sectionLabels[
                    section
                  ] && (
                    <p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
                      {
                        sectionLabels[
                          section
                        ]
                      }
                    </p>
                  )}


                  <div className="space-y-1">

                    {items.map(
                      (item) => {
                        const Icon =
                          item.icon;

                        const active =
                          isActive(
                            item.href,
                          );


                        return (
                          <Link
                            key={
                              item.href
                            }
                            href={
                              item.href
                            }
                            className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition ${
                              active
                                ? "bg-blue-600 text-white shadow-sm"
                                : "text-slate-700 hover:bg-slate-100 hover:text-slate-900"
                            }`}
                          >
                            <Icon className="h-5 w-5 shrink-0" />

                            <span className="truncate">
                              {
                                item.label
                              }
                            </span>

                          </Link>
                        );
                      },
                    )}

                  </div>

                </div>
              );
            },
          )}

        </div>

      </nav>

    </aside>
  );
}