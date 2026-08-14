"use client";

import {
  useEffect,
  useState,
} from "react";

import type {
  FormEvent,
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
  useUpdateTenantAdmin,
} from "../hooks";

import type {
  TenantAdmin,
} from "../types";


type Props = {
  tenantId: string;
  admin: TenantAdmin;
};


export default function EditTenantAdminDialog({
  tenantId,
  admin,
}: Props) {
  const mutation =
    useUpdateTenantAdmin(
      tenantId,
    );

  const [
    open,
    setOpen,
  ] = useState(false);

  const [
    firstName,
    setFirstName,
  ] = useState(
    admin.first_name,
  );

  const [
    lastName,
    setLastName,
  ] = useState(
    admin.last_name,
  );

  const [
    isActive,
    setIsActive,
  ] = useState(
    admin.is_active,
  );


  useEffect(() => {
    if (!open) {
      return;
    }

    setFirstName(
      admin.first_name,
    );

    setLastName(
      admin.last_name,
    );

    setIsActive(
      admin.is_active,
    );
  }, [
    open,
    admin,
  ]);


  async function submit(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    try {
      await mutation.mutateAsync({
        userId:
          admin.id,

        data: {
          first_name:
            firstName.trim(),

          last_name:
            lastName.trim(),

          is_active:
            isActive,
        },
      });

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
        variant="outline"
        onClick={() =>
          setOpen(
            true,
          )
        }
        className="h-8 px-3 text-xs"
      >
        <Pencil className="mr-2 h-3.5 w-3.5" />

        Edit
      </Button>


      <Dialog
        open={
          open
        }
        onOpenChange={
          setOpen
        }
      >
        <DialogContent className="sm:max-w-lg">

          <DialogHeader>

            <DialogTitle>
              Edit Tenant Administrator
            </DialogTitle>

            <DialogDescription>
              Update administrator
              account details and status.
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
                value={
                  admin.email
                }
                disabled
                className="mt-2 h-10 w-full rounded-md border border-slate-200 bg-slate-50 px-3 text-sm text-slate-500"
              />

              <p className="mt-1 text-xs text-slate-400">
                Email cannot be changed
                from this screen.
              </p>
            </div>


            <label className="flex items-center gap-2 text-sm text-slate-700">

              <input
                type="checkbox"
                checked={
                  isActive
                }
                onChange={(
                  event,
                ) =>
                  setIsActive(
                    event.target.checked,
                  )
                }
              />

              Active administrator

            </label>


            {mutation.isError && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                Failed to update
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
                  setOpen(
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
                  !lastName.trim()
                }
              >
                {
                  mutation.isPending
                    ? "Saving..."
                    : "Save Changes"
                }
              </Button>

            </DialogFooter>

          </form>

        </DialogContent>
      </Dialog>
    </>
  );
}