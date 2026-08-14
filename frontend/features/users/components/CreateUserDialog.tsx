// features/users/components/CreateUserDialog.tsx

"use client";

import {
  FormEvent,
  useState,
} from "react";

import {
  UserPlus,
} from "lucide-react";

import {
  useCreateUser,
} from "../hooks";


export default function CreateUserDialog() {
  const mutation =
    useCreateUser();

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

    setFirstName("");
    setLastName("");
    setEmail("");
    setPassword("");

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
        <UserPlus className="h-4 w-4" />

        Create User
      </button>
    );
  }


  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm">

      <div className="flex items-center justify-between">

        <h2 className="text-lg font-semibold">
          Create User
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
          <p className="text-sm text-red-600">
            Failed to create user.
          </p>
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
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {mutation.isPending
            ? "Creating..."
            : "Create User"}
        </button>

      </form>

    </div>
  );
}