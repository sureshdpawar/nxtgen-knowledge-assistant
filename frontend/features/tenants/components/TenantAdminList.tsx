import {
  ShieldCheck,
  User,
} from "lucide-react";

import type {
  TenantAdmin,
} from "../types";

import EditTenantAdminDialog from "./EditTenantAdminDialog";


type Props = {
  tenantId: string;
  admins: TenantAdmin[];
};


export default function TenantAdminList({
  tenantId,
  admins,
}: Props) {
  if (
    admins.length === 0
  ) {
    return (
      <div className="rounded-xl border border-dashed bg-white p-8 text-center">

        <ShieldCheck className="mx-auto h-8 w-8 text-slate-300" />

        <h3 className="mt-3 font-semibold text-slate-900">
          No tenant administrators
        </h3>

        <p className="mt-2 text-sm text-slate-500">
          Create an administrator
          account for this tenant.
        </p>

      </div>
    );
  }


  return (
    <div className="space-y-3">

      {admins.map(
        (admin) => (
          <div
            key={
              admin.id
            }
            className="rounded-xl border bg-white p-5 shadow-sm"
          >

            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">

              <div className="flex min-w-0 items-start gap-3">

                <div className="rounded-full bg-blue-100 p-3">
                  <User className="h-5 w-5 text-blue-600" />
                </div>


                <div className="min-w-0">

                  <h3 className="font-semibold text-slate-900">
                    {admin.first_name}{" "}
                    {admin.last_name}
                  </h3>

                  <p className="mt-1 truncate text-sm text-slate-500">
                    {admin.email}
                  </p>

                  <p className="mt-2 break-all text-xs text-slate-400">
                    User ID:{" "}
                    {admin.id}
                  </p>

                </div>

              </div>


              <div className="flex flex-wrap items-center gap-2">

                <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
                  {admin.role}
                </span>


                <span
                  className={
                    admin.is_active
                      ? "rounded-full bg-green-50 px-3 py-1 text-xs font-medium text-green-700"
                      : "rounded-full bg-red-50 px-3 py-1 text-xs font-medium text-red-700"
                  }
                >
                  {admin.is_active
                    ? "ACTIVE"
                    : "INACTIVE"}
                </span>


                <EditTenantAdminDialog
                  tenantId={
                    tenantId
                  }
                  admin={
                    admin
                  }
                />

              </div>

            </div>

          </div>
        ),
      )}

    </div>
  );
}