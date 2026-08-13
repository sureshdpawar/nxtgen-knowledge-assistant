"use client";

import Link from "next/link";

import {
  useParams,
} from "next/navigation";

import {
  ChevronRight,
} from "lucide-react";

import {
  useTenant,
  useTenantAdmins,
} from "@/features/tenants/hooks";

import CreateTenantAdminDialog from "@/features/tenants/components/CreateTenantAdminDialog";
import EditTenantDialog from "@/features/tenants/components/EditTenantDialog";
import TenantAdminList from "@/features/tenants/components/TenantAdminList";


export default function TenantDetailPage() {
  const params =
    useParams<{
      id: string;
    }>();

  const id =
    params.id;


  const {
    data: tenant,
    isLoading,
    error,
  } =
    useTenant(id);


  const {
    data: admins,
    isLoading:
      adminsLoading,
    error:
      adminsError,
  } =
    useTenantAdmins(id);


  if (isLoading) {
    return (
      <p className="text-slate-500">
        Loading tenant...
      </p>
    );
  }


  if (
    error ||
    !tenant
  ) {
    return (
      <p className="text-red-600">
        Failed to load tenant.
      </p>
    );
  }


  return (
    <div className="space-y-8">

      <nav className="flex items-center gap-1 text-sm text-slate-500">

        <Link
          href="/tenants"
          className="hover:text-slate-900"
        >
          Tenants
        </Link>

        <ChevronRight className="h-4 w-4" />

        <span className="font-medium text-slate-900">
          Tenant Details
        </span>

      </nav>


      <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">

        <div>

          <p className="text-sm font-medium text-slate-500">
            Tenant Details
          </p>

          <h1 className="mt-1 text-3xl font-bold text-slate-900">
            {tenant.name}
          </h1>

          <p className="mt-2 text-slate-500">
            {tenant.slug}
          </p>


          <div className="mt-4 flex flex-wrap gap-3 text-xs text-slate-400">

            <span>
              Tenant ID:{" "}
              {tenant.id}
            </span>

            <span>•</span>

            <span>
              Plan:{" "}
              {tenant.plan}
            </span>

            <span>•</span>

            <span>
              Status:{" "}
              {tenant.status}
            </span>

          </div>

        </div>


        <EditTenantDialog
          tenant={
            tenant
          }
        />

      </div>


      <section className="space-y-4">

        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">

          <div>

            <h2 className="text-xl font-semibold text-slate-900">
              Tenant Administrators
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Administrators who can
              manage this tenant.
            </p>

          </div>


          <CreateTenantAdminDialog
            tenantId={
              tenant.id
            }
          />

        </div>


        {adminsLoading && (
          <p className="text-sm text-slate-500">
            Loading tenant administrators...
          </p>
        )}


        {adminsError && (
          <p className="text-sm text-red-600">
            Failed to load tenant administrators.
          </p>
        )}


        {admins && (
          <TenantAdminList
            tenantId={
              tenant.id
            }
            admins={
              admins
            }
          />
        )}

      </section>

    </div>
  );
}