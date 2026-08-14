"use client";

import {
  FormEvent,
  useState,
} from "react";

import {
  UserPlus,
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


  function resetForm() {
    setFirstName("");
    setLastName("");
    setEmail("");
    setPassword("");
  }


  function handleOpenChange(
    nextOpen: boolean,
  ) {
    setOpen(nextOpen);

    if (!nextOpen) {
      resetForm();
    }
  }


  async function submit(
    event: FormEvent,
  ) {
    event.preventDefault();

    try {
      await mutation.mutateAsync({
        first_name:
          firstName.trim(),

        last_name:
          lastName.trim(),

        email:
          email.trim(),

        password,
      });

      resetForm();
      setOpen(false);

    } catch {
      // Mutation error is rendered below.
    }
  }


  return (
    <>
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


      <Dialog
        open={open}
        onOpenChange={
          handleOpenChange
        }
      >
        <DialogContent className="sm:max-w-lg">

          <DialogHeader>

            <DialogTitle>
              Create User
            </DialogTitle>

            <DialogDescription>
              Create a new user account
              for your tenant. The account
              will automatically have the
              USER role.
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
                  placeholder="John"
                  autoComplete="given-name"
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
                  placeholder="Doe"
                  autoComplete="family-name"
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
                value={
                  email
                }
                onChange={(event) =>
                  setEmail(
                    event.target.value,
                  )
                }
                placeholder="john@example.com"
                autoComplete="email"
                className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm outline-none focus:border-blue-500"
              />

            </div>


            <div>

              <label className="text-sm font-medium text-slate-700">
                Password
              </label>

              <input
                type="password"
                value={
                  password
                }
                onChange={(event) =>
                  setPassword(
                    event.target.value,
                  )
                }
                placeholder="Enter password"
                autoComplete="new-password"
                className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm outline-none focus:border-blue-500"
              />

              <p className="mt-1 text-xs text-slate-400">
                The user can change
                their password later
                once that feature is
                available.
              </p>

            </div>


            <div className="rounded-lg border bg-slate-50 p-4">

              <div className="flex items-start gap-3">

                <UserPlus className="mt-0.5 h-4 w-4 text-slate-400" />

                <div>

                  <p className="text-sm font-medium text-slate-900">
                    USER role
                  </p>

                  <p className="mt-1 text-xs leading-5 text-slate-500">
                    This account will
                    only be able to
                    Search and Chat
                    against knowledge
                    bases assigned by
                    an administrator.
                  </p>

                </div>

              </div>

            </div>


            {mutation.isError && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                Failed to create user.
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
                  handleOpenChange(
                    false,
                  )
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
                  !email.trim() ||
                  !password
                }
              >
                {mutation.isPending
                  ? "Creating..."
                  : "Create User"}
              </Button>

            </DialogFooter>

          </form>

        </DialogContent>
      </Dialog>
    </>
  );
}