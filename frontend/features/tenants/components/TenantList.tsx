import type {
  Tenant,
} from "../types";

import TenantCard from "./TenantCard";


type Props = {
  tenants: Tenant[];
};


export default function TenantList({
  tenants,
}: Props) {
  if (
    tenants.length === 0
  ) {
    return (
      <div className="rounded-xl border border-dashed bg-white p-10 text-center">

        <h3 className="font-semibold text-slate-900">
          No tenants
        </h3>

        <p className="mt-2 text-sm text-slate-500">
          Create your first tenant
          to get started.
        </p>

      </div>
    );
  }


  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">

      {tenants.map(
        (tenant) => (
          <TenantCard
            key={
              tenant.id
            }
            tenant={
              tenant
            }
          />
        ),
      )}

    </div>
  );
}