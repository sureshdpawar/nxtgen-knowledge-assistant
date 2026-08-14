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
  ] = useState(false);

  const [
    name,
    setName,
  ] = useState(
    tenant.name,
  );

  const [
    plan,
    setPlan,
  ] = useState(
    tenant.plan,
  );

  const [
    tenantStatus,
    setTenantStatus,
  ] = useState(
    tenant.status,
  );


  useEffect(() => {
    if (!open) {
      return;
    }

    setName(
      tenant.name,
    );

    setPlan(
      tenant.plan,
    );

    setTenantStatus(
      tenant.status,
    );
  }, [
    open,
    tenant,
  ]);


  async function submit(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    try {
      await mutation.mutateAsync({
        id:
          tenant.id,

        data: {
          name:
            name.trim(),

          plan:
            plan.trim(),

          status:
            tenantStatus,
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
      >
        <Pencil className="mr-2 h-4 w-4" />

        Edit Tenant
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
              Edit Tenant
            </DialogTitle>

            <DialogDescription>
              Update tenant details,
              plan and status.
            </DialogDescription>

          </DialogHeader>


          <form
            onSubmit={
              submit
            }
            className="space-y-5"
          >

            <div>
              <label className="text-sm font-medium text-slate-700">
                Name
              </label>

              <input
                value={
                  name
                }
                onChange={(
                  event,
                ) =>
                  setName(
                    event.target.value,
                  )
                }
                className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm outline-none focus:border-blue-500"
                required
              />
            </div>


            <div>
              <label className="text-sm font-medium text-slate-700">
                Plan
              </label>

              <input
                value={
                  plan
                }
                onChange={(
                  event,
                ) =>
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
                onChange={(
                  event,
                ) =>
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
              <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                Failed to update tenant.
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
                  !name.trim()
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