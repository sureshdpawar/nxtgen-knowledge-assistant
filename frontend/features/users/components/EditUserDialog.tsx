"use client";

import {
  FormEvent,
  useEffect,
  useState,
} from "react";

import {
  Pencil,
} from "lucide-react";

import {
  Button,
} from "@/components/ui/button";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

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


  useEffect(() => {
    if (!open) {
      return;
    }

    setFirstName(
      user.first_name,
    );

    setLastName(
      user.last_name,
    );

    setIsActive(
      user.is_active,
    );
  }, [
    open,
    user.first_name,
    user.last_name,
    user.is_active,
  ]);


  const hasChanges =
    firstName.trim() !==
      user.first_name ||
    lastName.trim() !==
      user.last_name ||
    isActive !==
      user.is_active;


  async function submit(
    event: FormEvent,
  ) {
    event.preventDefault();

    try {
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

    } catch {
      // Mutation error is shown below.
    }
  }


  return (
    <>
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


      <Dialog
        open={open}
        onOpenChange={
          setOpen
        }
      >
        <DialogContent className="sm:max-w-lg">

          <DialogHeader>

            <DialogTitle>
              Edit User
            </DialogTitle>

            <DialogDescription>
              Update account details
              for{" "}
              <span className="font-medium text-slate-700">
                {user.email}
              </span>
              .
            </DialogDescription>

          </DialogHeader>


          <form
            onSubmit={submit}
            className="space-y-5"
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
                value={
                  user.email
                }
                disabled
                className="mt-2 h-10 w-full rounded-md border border-slate-200 bg-slate-50 px-3 text-sm text-slate-500"
              />

              <p className="mt-1 text-xs text-slate-400">
                Email cannot be changed
                from this screen.
              </p>

            </div>


            <div className="rounded-lg border bg-slate-50 p-4">

              <label className="flex items-center justify-between gap-4">

                <div>

                  <p className="text-sm font-medium text-slate-900">
                    Active User
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    Inactive users cannot
                    sign in.
                  </p>

                </div>


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
                  className="h-4 w-4"
                />

              </label>

            </div>


            {mutation.isError && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                Failed to update user.
              </div>
            )}


            <DialogFooter>

              <Button
                type="button"
                variant="outline"
                disabled={
                  mutation.isPending
                }
                onClick={() =>
                  setOpen(false)
                }
              >
                Cancel
              </Button>


              <Button
                type="submit"
                disabled={
                  mutation.isPending ||
                  !firstName.trim() ||
                  !lastName.trim() ||
                  !hasChanges
                }
              >
                {mutation.isPending
                  ? "Saving..."
                  : "Save Changes"}
              </Button>

            </DialogFooter>

          </form>

        </DialogContent>
      </Dialog>
    </>
  );
}