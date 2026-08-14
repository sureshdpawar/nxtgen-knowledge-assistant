"use client";

import {
  useState,
} from "react";

import type {
  FormEvent,
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
  ] = useState(false);

  const [
    firstName,
    setFirstName,
  ] = useState("");

  const [
    lastName,
    setLastName,
  ] = useState("");

  const [
    email,
    setEmail,
  ] = useState("");

  const [
    password,
    setPassword,
  ] = useState("");


  function resetForm() {
    setFirstName("");
    setLastName("");
    setEmail("");
    setPassword("");
  }


  function handleOpenChange(
    nextOpen: boolean,
  ) {
    setOpen(
      nextOpen,
    );

    if (!nextOpen) {
      resetForm();
    }
  }


  async function submit(
    event:
      FormEvent<HTMLFormElement>,
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

      setOpen(
        false,
      );
    } catch {
      // Error displayed below.
    }
  }


  return (
    <>
      <Button
        type="button"
        onClick={() =>
          setOpen(
            true,
          )
        }
      >
        <UserPlus className="mr-2 h-4 w-4" />

        Create Tenant Admin
      </Button>


      <Dialog
        open={
          open
        }
        onOpenChange={
          handleOpenChange
        }
      >
        <DialogContent className="sm:max-w-lg">

          <DialogHeader>

            <DialogTitle>
              Create Tenant Admin
            </DialogTitle>

            <DialogDescription>
              Create an administrator
              account for this tenant.
            </DialogDescription>

          </DialogHeader>


          <form
            onSubmit={
              submit
            }
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
                  onChange={(
                    event,
                  ) =>
                    setFirstName(
                      event.target.value,
                    )
                  }
                  className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  required
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
                  onChange={(
                    event,
                  ) =>
                    setLastName(
                      event.target.value,
                    )
                  }
                  className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  required
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
                onChange={(
                  event,
                ) =>
                  setEmail(
                    event.target.value,
                  )
                }
                className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                required
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
                onChange={(
                  event,
                ) =>
                  setPassword(
                    event.target.value,
                  )
                }
                autoComplete="new-password"
                className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                required
              />
            </div>


            {mutation.isError && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                Failed to create tenant
                administrator.
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
                {
                  mutation.isPending
                    ? "Creating..."
                    : "Create Admin"
                }
              </Button>

            </DialogFooter>

          </form>

        </DialogContent>
      </Dialog>
    </>
  );
}