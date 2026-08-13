"use client";

import {
  FormEvent,
  useState,
} from "react";

import {
  UserPlus,
} from "lucide-react";

import {
  useCreateTenantAdmin,
} from "../hooks";


type Props = {
  tenantId: string;
};


export default function CreateTenantAdminDialog({
  tenantId,
}: Props) {
  const mutation =
    useCreateTenantAdmin(
      tenantId,
    );


  const [
    open,
    setOpen,
  ] =
    useState(false);


  const [
    firstName,
    setFirstName,
  ] =
    useState("");


  const [
    lastName,
    setLastName,
  ] =
    useState("");


  const [
    email,
    setEmail,
  ] =
    useState("");


  const [
    password,
    setPassword,
  ] =
    useState("");


  const [
    created,
    setCreated,
  ] =
    useState(false);


  async function submit(
    event: FormEvent,
  ) {
    event.preventDefault();

    await mutation.mutateAsync({
      first_name:
        firstName.trim(),

      last_name:
        lastName.trim(),

      email:
        email.trim(),

      password,
    });

    setCreated(true);

    setFirstName("");
    setLastName("");
    setEmail("");
    setPassword("");
  }


  if (!open) {
    return (
      <button
        type="button"
        onClick={() => {
          setOpen(true);
          setCreated(false);
        }}
        className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
      >
        <UserPlus className="h-4 w-4" />

        Create Tenant Admin
      </button>
    );
  }


  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm">

      <div className="flex items-center justify-between">

        <h2 className="text-lg font-semibold">
          Create Tenant Admin
        </h2>


        <button
          type="button"
          onClick={() =>
            setOpen(false)
          }
          className="text-sm text-slate-500 hover:text-slate-900"
        >
          Close
        </button>

      </div>


      {created && (
        <div className="mt-4 rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-700">
          Tenant admin created successfully.
        </div>
      )}


      <form
        onSubmit={submit}
        className="mt-5 space-y-4"
      >

        <div className="grid gap-4 md:grid-cols-2">

          <div>

            <label className="text-sm font-medium text-slate-700">
              First Name
            </label>

            <input
              value={
                firstName
              }
              onChange={(event) =>
                setFirstName(
                  event.target.value,
                )
              }
              className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm outline-none focus:border-blue-500"
            />

          </div>


          <div>

            <label className="text-sm font-medium text-slate-700">
              Last Name
            </label>

            <input
              value={
                lastName
              }
              onChange={(event) =>
                setLastName(
                  event.target.value,
                )
              }
              className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm outline-none focus:border-blue-500"
            />

          </div>

        </div>


        <div>

          <label className="text-sm font-medium text-slate-700">
            Email
          </label>

          <input
            type="email"
            value={email}
            onChange={(event) =>
              setEmail(
                event.target.value,
              )
            }
            className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm outline-none focus:border-blue-500"
          />

        </div>


        <div>

          <label className="text-sm font-medium text-slate-700">
            Password
          </label>

          <input
            type="password"
            value={password}
            onChange={(event) =>
              setPassword(
                event.target.value,
              )
            }
            className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm outline-none focus:border-blue-500"
          />

        </div>


        {mutation.isError && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            Failed to create tenant admin.
          </div>
        )}


        <button
          type="submit"
          disabled={
            mutation.isPending ||
            !firstName.trim() ||
            !lastName.trim() ||
            !email.trim() ||
            !password
          }
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {mutation.isPending
            ? "Creating..."
            : "Create Admin"}
        </button>

      </form>

    </div>
  );
}