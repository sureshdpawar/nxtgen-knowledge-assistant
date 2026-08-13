"use client";

import {
  FormEvent,
  useState,
} from "react";

import {
  Plus,
} from "lucide-react";

import {
  useCreateTenant,
} from "../hooks";


export default function CreateTenantDialog() {
  const mutation =
    useCreateTenant();


  const [
    open,
    setOpen,
  ] =
    useState(false);


  const [
    name,
    setName,
  ] =
    useState("");


  const [
    slug,
    setSlug,
  ] =
    useState("");


  async function submit(
    event: FormEvent,
  ) {
    event.preventDefault();

    if (
      !name.trim() ||
      !slug.trim()
    ) {
      return;
    }

    await mutation.mutateAsync({
      name:
        name.trim(),

      slug:
        slug
          .trim()
          .toLowerCase(),
    });

    setName("");
    setSlug("");

    setOpen(false);
  }


  if (!open) {
    return (
      <button
        type="button"
        onClick={() =>
          setOpen(true)
        }
        className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
      >
        <Plus className="h-4 w-4" />

        Create Tenant
      </button>
    );
  }


  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm">

      <div className="flex items-center justify-between">

        <h2 className="text-lg font-semibold">
          Create Tenant
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
            Tenant Name
          </label>

          <input
            value={name}
            onChange={(event) =>
              setName(
                event.target.value,
              )
            }
            placeholder="Acme Corporation"
            className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm outline-none focus:border-blue-500"
          />

        </div>


        <div>

          <label className="text-sm font-medium text-slate-700">
            Slug
          </label>

          <input
            value={slug}
            onChange={(event) =>
              setSlug(
                event.target.value,
              )
            }
            placeholder="acme"
            className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm outline-none focus:border-blue-500"
          />

        </div>


        {mutation.isError && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            Failed to create tenant.
          </div>
        )}


        <button
          type="submit"
          disabled={
            mutation.isPending ||
            !name.trim() ||
            !slug.trim()
          }
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {mutation.isPending
            ? "Creating..."
            : "Create Tenant"}
        </button>

      </form>

    </div>
  );
}