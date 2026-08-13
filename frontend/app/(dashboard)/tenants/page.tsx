"use client";

import {
  useTenants,
} from "@/features/tenants/hooks";

import CreateTenantDialog from "@/features/tenants/components/CreateTenantDialog";
import TenantList from "@/features/tenants/components/TenantList";


export default function TenantsPage() {
  const {
    data,
    isLoading,
    error,
  } =
    useTenants();


  return (
    <div className="space-y-8">

      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">

        <div>

          <p className="text-sm font-medium text-slate-500">
            Platform Administration
          </p>

          <h1 className="mt-1 text-3xl font-bold text-slate-900">
            Tenants
          </h1>

          <p className="mt-2 text-slate-500">
            Manage organizations
            using the platform.
          </p>

        </div>


        <CreateTenantDialog />

      </div>


      {isLoading && (
        <p className="text-sm text-slate-500">
          Loading tenants...
        </p>
      )}


      {error && (
        <p className="text-sm text-red-600">
          Failed to load tenants.
        </p>
      )}


      {data && (
        <TenantList
          tenants={data}
        />
      )}

    </div>
  );
}