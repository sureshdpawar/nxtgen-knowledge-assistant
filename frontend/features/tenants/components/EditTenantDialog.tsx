"use client";

import {
  FormEvent,
  useState,
} from "react";

import {
  Pencil,
} from "lucide-react";

import {
  useUpdateTenant,
} from "../hooks";

import type {
  Tenant,
} from "../types";


type Props = {
  tenant: Tenant;
};


export default function EditTenantDialog({
  tenant,
}: Props) {
  const mutation =
    useUpdateTenant();


  const [
    open,
    setOpen,
  ] =
    useState(false);


  const [
    name,
    setName,
  ] =
    useState(
      tenant.name,
    );


  const [
    plan,
    setPlan,
  ] =
    useState(
      tenant.plan,
    );


  const [
    tenantStatus,
    setTenantStatus,
  ] =
    useState(
      tenant.status,
    );


  async function submit(
    event: FormEvent,
  ) {
    event.preventDefault();

    await mutation.mutateAsync({
      id:
        tenant.id,

      data: {
        name:
          name.trim(),

        plan:
          plan.trim(),

        status:
          tenantStatus.trim(),
      },
    });

    setOpen(false);
  }


  if (!open) {
    return (
      <button
        type="button"
        onClick={() =>
          setOpen(true)
        }
        className="flex items-center gap-2 rounded-lg border bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
      >
        <Pencil className="h-4 w-4" />

        Edit Tenant
      </button>
    );
  }


  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm">

      <div className="flex items-center justify-between">

        <h2 className="text-lg font-semibold">
          Edit Tenant
        </h2>

        <button
          type="button"
          onClick={() =>
            setOpen(false)
          }
          className="text-sm text-slate-500 hover:text-slate-900"
        >
          Cancel
        </button>

      </div>


      <form
        onSubmit={submit}
        className="mt-5 space-y-4"
      >

        <div>

          <label className="text-sm font-medium text-slate-700">
            Name
          </label>

          <input
            value={name}
            onChange={(event) =>
              setName(
                event.target.value,
              )
            }
            className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm outline-none focus:border-blue-500"
          />

        </div>


        <div>

          <label className="text-sm font-medium text-slate-700">
            Plan
          </label>

          <input
            value={plan}
            onChange={(event) =>
              setPlan(
                event.target.value,
              )
            }
            className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm outline-none focus:border-blue-500"
          />

        </div>


        <div>

          <label className="text-sm font-medium text-slate-700">
            Status
          </label>

          <select
            value={
              tenantStatus
            }
            onChange={(event) =>
              setTenantStatus(
                event.target.value,
              )
            }
            className="mt-2 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
          >
            <option value="active">
              Active
            </option>

            <option value="inactive">
              Inactive
            </option>
          </select>

        </div>


        {mutation.isError && (
          <p className="text-sm text-red-600">
            Failed to update tenant.
          </p>
        )}


        <button
          type="submit"
          disabled={
            mutation.isPending ||
            !name.trim()
          }
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {mutation.isPending
            ? "Saving..."
            : "Save Changes"}
        </button>

      </form>

    </div>
  );
}