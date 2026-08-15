"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import {
  Building2,
  Database,
  LayoutDashboard,
  MessageSquare,
  Search,
  Settings,
  Users,
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
  },

  {
    label: "Tenants",
    href: "/tenants",
    icon: Building2,
    roles: [
      "SUPERADMIN",
    ],
  },

  {
    label: "Knowledge Bases",
    href: "/knowledge-bases",
    icon: Database,
    roles: [
      "ADMIN",
    ],
  },

  {
    label: "Users",
    href: "/users",
    icon: Users,
    roles: [
      "ADMIN",
    ],
  },

  {
    label: "Search",
    href: "/search",
    icon: Search,
    roles: [
      "ADMIN",
      "USER",
    ],
  },

  {
    label: "Chat",
    href: "/chat",
    icon: MessageSquare,
    roles: [
      "ADMIN",
      "USER",
    ],
  },

  {
    label: "LLM Profiles",
    href: "/settings",
    icon: Settings,
    roles: [
      "ADMIN",
    ],
  },
];


export default function Sidebar() {
  const pathname =
    usePathname();

  const {
    user,
  } =
    useAuth();


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


  return (
    <aside className="w-64 border-r bg-white">

      <div className="border-b px-4 py-3">

        <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
          Signed in as
        </p>

        <p className="mt-1 truncate text-sm font-semibold text-slate-800">
          {user.first_name}{" "}
          {user.last_name}
        </p>

        <p className="mt-1 text-xs text-slate-500">
          {user.role}
        </p>

      </div>


      <nav className="space-y-2 p-4">

        {visibleMenu.map(
          (item) => {
            const Icon =
              item.icon;

            const active =
              pathname ===
                item.href ||
              pathname.startsWith(
                `${item.href}/`,
              );


            return (
              <Link
                key={
                  item.href
                }
                href={
                  item.href
                }
                className={`flex items-center gap-3 rounded-lg px-3 py-2 transition ${
                  active
                    ? "bg-blue-600 text-white shadow"
                    : "text-slate-700 hover:bg-slate-100"
                }`}
              >
                <Icon className="h-5 w-5" />

                <span>
                  {
                    item.label
                  }
                </span>
              </Link>
            );
          },
        )}

      </nav>

    </aside>
  );
}