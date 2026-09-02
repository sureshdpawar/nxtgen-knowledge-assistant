"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import {
  Activity,
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
  X,
} from "lucide-react";

import { useAuth } from "@/hooks/useAuth";

import type { UserRole } from "@/types/auth";


type SidebarProps = {
  mobile?: boolean;
  onNavigate?: () => void;
  onClose?: () => void;
};


type MenuItem = {
  label: string;

  href: string;

  icon: React.ComponentType<{
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
    label: "Online Evaluation",
    href: "/online-evaluation",
    icon: Activity,
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
    section: "administration",
  },

  {
    label: "Users",
    href: "/users",
    icon: Users,
    roles: [
      "ADMIN",
    ],
    section: "administration",
  },

  {
    label: "Usage & Limits",
    href: "/usage",
    icon: Gauge,
    roles: [
      "ADMIN",
    ],
    section: "administration",
  },

  {
    label: "LLM Profiles",
    href: "/settings",
    icon: BrainCircuit,
    roles: [
      "ADMIN",
    ],
    section: "administration",
  },
];


const sectionLabels = {
  main: "",
  knowledge: "Knowledge",
  studio: "Agent Studio",
  administration: "Administration",
} as const;


const sectionOrder:
  MenuItem["section"][] = [
    "main",
    "knowledge",
    "studio",
    "administration",
  ];


export default function Sidebar({
  mobile = false,
  onNavigate,
  onClose,
}: SidebarProps) {
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


  function handleNavigate() {
    if (mobile) {
      onNavigate?.();
    }
  }


  return (
    <aside
      className={`
        flex
        h-full
        flex-col
        bg-white
        ${
          mobile
            ? "w-full"
            : "w-64 border-r border-slate-200"
        }
      `}
    >

      {/*
       * Mobile drawer header
       */}
      {mobile && (
        <div
          className="
            flex
            h-16
            shrink-0
            items-center
            justify-between
            border-b
            border-slate-200
            px-4
          "
        >
          <div className="min-w-0">
            <p
              className="
                truncate
                text-base
                font-semibold
                text-slate-900
              "
            >
              Knowgentiq
            </p>

            <p
              className="
                text-xs
                text-slate-500
              "
            >
              Navigation
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            aria-label="Close navigation menu"
            className="
              inline-flex
              h-10
              w-10
              shrink-0
              items-center
              justify-center
              rounded-lg
              text-slate-600
              transition
              hover:bg-slate-100
              hover:text-slate-900
              focus:outline-none
              focus:ring-2
              focus:ring-slate-300
            "
          >
            <X className="h-5 w-5" />
          </button>
        </div>
      )}


      {/*
       * Signed-in user
       */}
      <div
        className="
          shrink-0
          border-b
          border-slate-200
          px-4
          py-3
        "
      >

        <p
          className="
            text-[11px]
            font-medium
            uppercase
            tracking-wide
            text-slate-400
          "
        >
          Signed in as
        </p>


        <p
          className="
            mt-1
            truncate
            text-sm
            font-semibold
            text-slate-800
          "
        >
          {user.first_name}{" "}
          {user.last_name}
        </p>


        <div
          className="
            mt-1
            flex
            min-w-0
            items-center
            gap-1.5
            text-xs
          "
        >

          <span
            className="
              shrink-0
              font-semibold
              text-slate-600
            "
          >
            {user.role}
          </span>


          {showTenant && (
            <>
              <span className="text-slate-300">
                ·
              </span>

              <span
                className="
                  min-w-0
                  truncate
                  font-medium
                  text-slate-500
                "
              >
                {user.tenant_name}
              </span>
            </>
          )}

        </div>

      </div>


      {/*
       * Navigation
       */}
      <nav
        className="
          min-h-0
          flex-1
          overflow-y-auto
          overscroll-contain
          p-4
        "
      >

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
                  key={section}
                >

                  {sectionLabels[
                    section
                  ] && (
                    <p
                      className="
                        mb-2
                        px-3
                        text-xs
                        font-semibold
                        uppercase
                        tracking-wider
                        text-slate-400
                      "
                    >
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
                            onClick={
                              handleNavigate
                            }
                            aria-current={
                              active
                                ? "page"
                                : undefined
                            }
                            className={`
                              flex
                              min-h-11
                              items-center
                              gap-3
                              rounded-lg
                              px-3
                              py-2.5
                              text-sm
                              font-medium
                              transition
                              ${
                                active
                                  ? "bg-blue-600 text-white shadow-sm"
                                  : "text-slate-700 hover:bg-slate-100 hover:text-slate-900"
                              }
                            `}
                          >

                            <Icon
                              className="
                                h-5
                                w-5
                                shrink-0
                              "
                            />

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
