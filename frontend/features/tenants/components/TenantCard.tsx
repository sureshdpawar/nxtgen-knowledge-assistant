"use client";

import Link from "next/link";

import {
  Building2,
  ChevronRight,
} from "lucide-react";

import type {
  Tenant,
} from "../types";


type Props = {
  tenant: Tenant;
};


export default function TenantCard({
  tenant,
}: Props) {
  return (
    <Link
      href={
        `/tenants/${tenant.id}`
      }
      className="block rounded-xl border bg-white p-6 shadow-sm transition hover:shadow-md"
    >

      <div className="flex items-start justify-between gap-4">

        <div className="flex items-start gap-3">

          <div className="rounded-lg bg-blue-100 p-3">
            <Building2 className="h-5 w-5 text-blue-600" />
          </div>


          <div>

            <h2 className="text-lg font-semibold text-slate-900">
              {tenant.name}
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              {tenant.slug}
            </p>

          </div>

        </div>


        <ChevronRight className="h-5 w-5 text-slate-400" />

      </div>


      <div className="mt-5 flex flex-wrap gap-2">

        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
          Plan: {tenant.plan}
        </span>

        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
          Status: {tenant.status}
        </span>

      </div>


      <p className="mt-4 break-all text-xs text-slate-400">
        Tenant ID:{" "}
        {tenant.id}
      </p>

    </Link>
  );
}