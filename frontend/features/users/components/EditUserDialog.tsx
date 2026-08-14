// features/users/components/EditUserDialog.tsx

"use client";

import {
  FormEvent,
  useState,
} from "react";

import {
  Pencil,
} from "lucide-react";

import {
  useUpdateUser,
} from "../hooks";

import type {
  User,
} from "../types";


type Props = {
  user: User;
};


export default function EditUserDialog({
  user,
}: Props) {
  const mutation =
    useUpdateUser();

  const [
    open,
    setOpen,
  ] =
    useState(false);

  const [
    firstName,
    setFirstName,
  ] =
    useState(
      user.first_name,
    );

  const [
    lastName,
    setLastName,
  ] =
    useState(
      user.last_name,
    );

  const [
    isActive,
    setIsActive,
  ] =
    useState(
      user.is_active,
    );


  async function submit(
    event: FormEvent,
  ) {
    event.preventDefault();

    await mutation.mutateAsync({
      id:
        user.id,

      data: {
        first_name:
          firstName.trim(),

        last_name:
          lastName.trim(),

        is_active:
          isActive,
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
        className="flex items-center gap-2 rounded-md border px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-100"
      >
        <Pencil className="h-3.5 w-3.5" />

        Edit
      </button>
    );
  }


  return (
    <div className="mt-4 rounded-lg border bg-slate-50 p-4">

      <div className="flex items-center justify-between">

        <h4 className="font-medium text-slate-900">
          Edit User
        </h4>

        <button
          type="button"
          onClick={() =>
            setOpen(false)
          }
          className="text-xs text-slate-500"
        >
          Cancel
        </button>

      </div>


      <form
        onSubmit={submit}
        className="mt-4 space-y-4"
      >

        <div className="grid gap-4 md:grid-cols-2">

          <input
            value={
              firstName
            }
            onChange={(event) =>
              setFirstName(
                event.target.value,
              )
            }
            placeholder="First name"
            className="h-10 rounded-md border bg-white px-3 text-sm"
          />


          <input
            value={
              lastName
            }
            onChange={(event) =>
              setLastName(
                event.target.value,
              )
            }
            placeholder="Last name"
            className="h-10 rounded-md border bg-white px-3 text-sm"
          />

        </div>


        <label className="flex items-center gap-2 text-sm text-slate-700">

          <input
            type="checkbox"
            checked={
              isActive
            }
            onChange={(event) =>
              setIsActive(
                event.target.checked,
              )
            }
          />

          Active user

        </label>


        {mutation.isError && (
          <p className="text-sm text-red-600">
            Failed to update user.
          </p>
        )}


        <button
          type="submit"
          disabled={
            mutation.isPending
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