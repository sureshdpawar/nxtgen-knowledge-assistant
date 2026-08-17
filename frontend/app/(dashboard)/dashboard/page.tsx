"use client";

import {
  useEffect,
} from "react";

import Link from "next/link";

import {
  useRouter,
} from "next/navigation";

import {
  Bot,
  Building2,
  Cable,
  ChevronRight,
  Database,
  FileText,
  Library,
  Settings,
  ShieldCheck,
  UserCheck,
  Users,
  Wrench,
} from "lucide-react";

import {
  useAuth,
} from "@/hooks/useAuth";

import {
  useAgents,
} from "@/features/agents/hooks";

import {
  useDashboardStats,
  usePlatformDashboardStats,
} from "@/features/dashboard/hooks";

import {
  useIntegrations,
} from "@/features/integrations/hooks";

import {
  useKnowledgeBases,
} from "@/features/knowledge-bases/hooks";

import {
  useLLMProfiles,
} from "@/features/llm-config/hooks";

import {
  useTenants,
} from "@/features/tenants/hooks";

import {
  useTools,
} from "@/features/tools/hooks";

import {
  useUsers,
} from "@/features/users/hooks";


export default function DashboardPage() {
  const router =
    useRouter();

  const {
    user,
  } =
    useAuth();


  const isAdmin =
    user?.role === "ADMIN";

  const isSuperAdmin =
    user?.role === "SUPERADMIN";

  const isUser =
    user?.role === "USER";


  const {
    data:
      adminStats,

    isLoading:
      adminStatsLoading,

    error:
      adminStatsError,
  } =
    useDashboardStats(
      isAdmin,
    );


  const {
    data:
      platformStats,

    isLoading:
      platformStatsLoading,

    error:
      platformStatsError,
  } =
    usePlatformDashboardStats(
      isSuperAdmin,
    );


  const {
    data:
      users,

    isLoading:
      usersLoading,
  } =
    useUsers(
      isAdmin,
    );


  const {
    data:
      knowledgeBases,

    isLoading:
      knowledgeBasesLoading,
  } =
    useKnowledgeBases(
      isAdmin,
    );


  const {
    data:
      tenants,

    isLoading:
      tenantsLoading,
  } =
    useTenants(
      isSuperAdmin,
    );


  const {
    data:
      agents,

    isLoading:
      agentsLoading,

    isError:
      agentsError,
  } =
    useAgents(
      isAdmin,
    );


  const {
    data:
      integrations,

    isLoading:
      integrationsLoading,

    isError:
      integrationsError,
  } =
    useIntegrations(
      isAdmin,
    );


  const {
    data:
      tools,

    isLoading:
      toolsLoading,

    isError:
      toolsError,
  } =
    useTools(
      isAdmin,
    );


  const {
    data:
      llmProfiles,

    isLoading:
      llmProfilesLoading,

    isError:
      llmProfilesError,
  } =
    useLLMProfiles(
      isAdmin,
    );


  useEffect(() => {
    if (
      isUser
    ) {
      router.replace(
        "/chat",
      );
    }
  }, [
    isUser,
    router,
  ]);


  if (!user) {
    return null;
  }


  if (isUser) {
    return null;
  }


  if (isSuperAdmin) {
    const recentTenants =
      [...(
        tenants ?? []
      )]
        .sort(
          (
            left,
            right,
          ) =>
            new Date(
              right.created_at,
            ).getTime() -
            new Date(
              left.created_at,
            ).getTime(),
        )
        .slice(
          0,
          5,
        );


    const loading =
      platformStatsLoading ||
      tenantsLoading;


    return (
      <div className="space-y-8">

        <div>

          <p className="text-sm font-medium text-slate-500">
            Platform Administration
          </p>

          <h1 className="mt-1 text-3xl font-bold text-slate-900">
            Dashboard
          </h1>

          <p className="mt-2 text-slate-500">
            Welcome back,{" "}
            {user.first_name}.
          </p>

        </div>


        {platformStatsError && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            Failed to load platform
            statistics.
          </div>
        )}


        {loading ? (
          <p className="text-sm text-slate-500">
            Loading dashboard...
          </p>
        ) : (
          <>

            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">

              <StatCard
                label="Total Tenants"
                value={
                  platformStats
                    ?.total_tenants ??
                  0
                }
                icon={
                  Building2
                }
                href="/tenants"
              />


              <StatCard
                label="Active Tenants"
                value={
                  platformStats
                    ?.active_tenants ??
                  0
                }
                icon={
                  UserCheck
                }
                href="/tenants"
              />


              <StatCard
                label="Tenant Admins"
                value={
                  platformStats
                    ?.total_admins ??
                  0
                }
                icon={
                  ShieldCheck
                }
              />


              <StatCard
                label="Platform Users"
                value={
                  platformStats
                    ?.total_users ??
                  0
                }
                icon={
                  Users
                }
              />

            </div>


            <section className="rounded-xl border bg-white shadow-sm">

              <div className="flex items-center justify-between border-b px-6 py-5">

                <div>

                  <h2 className="font-semibold text-slate-900">
                    Recent Tenants
                  </h2>

                  <p className="mt-1 text-sm text-slate-500">
                    Recently created
                    organizations.
                  </p>

                </div>


                <Link
                  href="/tenants"
                  className="flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-700"
                >
                  View all

                  <ChevronRight className="h-4 w-4" />
                </Link>

              </div>


              {recentTenants.length ===
              0 ? (
                <div className="p-6 text-sm text-slate-500">
                  No tenants yet.
                </div>
              ) : (
                <div className="divide-y">

                  {recentTenants.map(
                    (
                      tenant,
                    ) => (
                      <Link
                        key={
                          tenant.id
                        }
                        href={
                          `/tenants/${tenant.id}`
                        }
                        className="flex items-center justify-between gap-4 px-6 py-4 hover:bg-slate-50"
                      >

                        <div className="min-w-0">

                          <p className="truncate text-sm font-medium text-slate-900">
                            {
                              tenant.name
                            }
                          </p>

                          <p className="mt-1 truncate text-xs text-slate-500">
                            {
                              tenant.slug
                            }
                          </p>

                        </div>


                        <div className="flex shrink-0 items-center gap-3">

                          <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
                            {
                              tenant.plan
                            }
                          </span>


                          <span
                            className={
                              tenant.status ===
                              "active"
                                ? "rounded-full bg-green-50 px-2.5 py-1 text-xs font-medium text-green-700"
                                : "rounded-full bg-red-50 px-2.5 py-1 text-xs font-medium text-red-700"
                            }
                          >
                            {
                              tenant.status
                            }
                          </span>


                          <ChevronRight className="h-4 w-4 text-slate-400" />

                        </div>

                      </Link>
                    ),
                  )}

                </div>
              )}

            </section>

          </>
        )}

      </div>
    );
  }


  const recentUsers =
    [...(
      users ?? []
    )]
      .sort(
        (
          left,
          right,
        ) =>
          new Date(
            right.created_at,
          ).getTime() -
          new Date(
            left.created_at,
          ).getTime(),
      )
      .slice(
        0,
        5,
      );


  const recentKnowledgeBases =
    [...(
      knowledgeBases ?? []
    )]
      .sort(
        (
          left,
          right,
        ) =>
          new Date(
            right.created_at,
          ).getTime() -
          new Date(
            left.created_at,
          ).getTime(),
      )
      .slice(
        0,
        5,
      );


  const loading =
    adminStatsLoading ||
    usersLoading ||
    knowledgeBasesLoading ||
    agentsLoading ||
    integrationsLoading ||
    toolsLoading ||
    llmProfilesLoading;


  const studioError =
    agentsError ||
    integrationsError ||
    toolsError ||
    llmProfilesError;


  return (
    <div className="space-y-8">

      <div>

        <p className="text-sm font-medium text-slate-500">
          Tenant Administration
        </p>

        <h1 className="mt-1 text-3xl font-bold text-slate-900">
          Dashboard
        </h1>

        <p className="mt-2 text-slate-500">
          Welcome back,{" "}
          {user.first_name}.
        </p>

      </div>


      {adminStatsError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Failed to load dashboard
          statistics.
        </div>
      )}


      {studioError && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-700">
          Some Agent Studio statistics
          could not be loaded.
        </div>
      )}


      {loading ? (
        <p className="text-sm text-slate-500">
          Loading dashboard...
        </p>
      ) : (
        <>

          <section>

            <div className="mb-4">

              <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Tenant Overview
              </p>

              <h2 className="mt-1 text-xl font-semibold text-slate-900">
                Knowledge & Users
              </h2>

            </div>


            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">

              <StatCard
                label="Total Users"
                value={
                  adminStats
                    ?.total_users ??
                  0
                }
                icon={
                  Users
                }
                href="/users"
              />


              <StatCard
                label="Active Users"
                value={
                  adminStats
                    ?.active_users ??
                  0
                }
                icon={
                  UserCheck
                }
                href="/users"
              />


              <StatCard
                label="Knowledge Bases"
                value={
                  adminStats
                    ?.knowledge_bases ??
                  0
                }
                icon={
                  Database
                }
                href="/knowledge-bases"
              />


              <StatCard
                label="Knowledge Sources"
                value={
                  adminStats
                    ?.knowledge_sources ??
                  0
                }
                icon={
                  Library
                }
                href="/knowledge-bases"
              />


              <StatCard
                label="Documents"
                value={
                  adminStats
                    ?.documents ??
                  0
                }
                icon={
                  FileText
                }
                href="/knowledge-bases"
              />

            </div>

          </section>


          <section>

            <div className="mb-4">

              <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Agent Studio
              </p>

              <h2 className="mt-1 text-xl font-semibold text-slate-900">
                AI Platform
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Manage agents, integrations,
                tools, and model profiles.
              </p>

            </div>


            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">

              <StatCard
                label="Agents"
                value={
                  agents?.length ??
                  0
                }
                icon={
                  Bot
                }
                href="/agents"
              />


              <StatCard
                label="Integrations"
                value={
                  integrations
                    ?.length ??
                  0
                }
                icon={
                  Cable
                }
                href="/integrations"
              />


              <StatCard
                label="Tools"
                value={
                  tools?.length ??
                  0
                }
                icon={
                  Wrench
                }
                href="/tools"
              />


              <StatCard
                label="LLM Profiles"
                value={
                  llmProfiles
                    ?.length ??
                  0
                }
                icon={
                  Settings
                }
                href="/settings"
              />

            </div>

          </section>


          <div className="grid gap-6 xl:grid-cols-2">

            <section className="rounded-xl border bg-white shadow-sm">

              <div className="flex items-center justify-between border-b px-6 py-5">

                <div>

                  <h2 className="font-semibold text-slate-900">
                    Recent Users
                  </h2>

                  <p className="mt-1 text-sm text-slate-500">
                    Recently created
                    tenant accounts.
                  </p>

                </div>


                <Link
                  href="/users"
                  className="flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-700"
                >
                  View all

                  <ChevronRight className="h-4 w-4" />
                </Link>

              </div>


              {recentUsers.length ===
              0 ? (
                <div className="p-6 text-sm text-slate-500">
                  No users yet.
                </div>
              ) : (
                <div className="divide-y">

                  {recentUsers.map(
                    (
                      recentUser,
                    ) => (
                      <div
                        key={
                          recentUser.id
                        }
                        className="flex items-center justify-between gap-4 px-6 py-4"
                      >

                        <div className="min-w-0">

                          <p className="truncate text-sm font-medium text-slate-900">
                            {
                              recentUser.first_name
                            }{" "}
                            {
                              recentUser.last_name
                            }
                          </p>

                          <p className="mt-1 truncate text-xs text-slate-500">
                            {
                              recentUser.email
                            }
                          </p>

                        </div>


                        <div className="flex shrink-0 items-center gap-2">

                          <span className="rounded-full bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700">
                            {
                              recentUser.role
                            }
                          </span>


                          <span
                            className={
                              recentUser.is_active
                                ? "rounded-full bg-green-50 px-2.5 py-1 text-xs font-medium text-green-700"
                                : "rounded-full bg-red-50 px-2.5 py-1 text-xs font-medium text-red-700"
                            }
                          >
                            {
                              recentUser.is_active
                                ? "ACTIVE"
                                : "INACTIVE"
                            }
                          </span>

                        </div>

                      </div>
                    ),
                  )}

                </div>
              )}

            </section>


            <section className="rounded-xl border bg-white shadow-sm">

              <div className="flex items-center justify-between border-b px-6 py-5">

                <div>

                  <h2 className="font-semibold text-slate-900">
                    Knowledge Bases
                  </h2>

                  <p className="mt-1 text-sm text-slate-500">
                    Recently created
                    knowledge bases.
                  </p>

                </div>


                <Link
                  href="/knowledge-bases"
                  className="flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-700"
                >
                  View all

                  <ChevronRight className="h-4 w-4" />
                </Link>

              </div>


              {recentKnowledgeBases.length ===
              0 ? (
                <div className="p-6 text-sm text-slate-500">
                  No knowledge bases yet.
                </div>
              ) : (
                <div className="divide-y">

                  {recentKnowledgeBases.map(
                    (
                      knowledgeBase,
                    ) => (
                      <Link
                        key={
                          knowledgeBase.id
                        }
                        href={
                          `/knowledge-bases/${knowledgeBase.id}`
                        }
                        className="flex items-center justify-between gap-4 px-6 py-4 hover:bg-slate-50"
                      >

                        <div className="min-w-0">

                          <p className="truncate text-sm font-medium text-slate-900">
                            {
                              knowledgeBase.name
                            }
                          </p>


                          {knowledgeBase.description && (
                            <p className="mt-1 truncate text-xs text-slate-500">
                              {
                                knowledgeBase.description
                              }
                            </p>
                          )}

                        </div>


                        <ChevronRight className="h-4 w-4 shrink-0 text-slate-400" />

                      </Link>
                    ),
                  )}

                </div>
              )}

            </section>

          </div>

        </>
      )}

    </div>
  );
}


type StatCardProps = {
  label: string;

  value: number;

  href?: string;

  icon:
    React.ComponentType<{
      className?: string;
    }>;
};


function StatCard({
  label,
  value,
  href,
  icon: Icon,
}: StatCardProps) {
  const content = (
    <div className="flex items-center justify-between gap-4">

      <div>

        <p className="text-sm font-medium text-slate-500">
          {label}
        </p>

        <p className="mt-2 text-3xl font-bold text-slate-900">
          {value}
        </p>

      </div>


      <div className="rounded-xl bg-blue-50 p-3">

        <Icon className="h-5 w-5 text-blue-600" />

      </div>

    </div>
  );


  if (!href) {
    return (
      <div className="rounded-xl border bg-white p-5 shadow-sm">
        {content}
      </div>
    );
  }


  return (
    <Link
      href={href}
      className="rounded-xl border bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
    >
      {content}
    </Link>
  );
}