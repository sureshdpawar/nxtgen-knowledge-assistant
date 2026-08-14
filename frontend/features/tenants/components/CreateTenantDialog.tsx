"use client";

import {
  useState,
} from "react";

import type {
  FormEvent,
} from "react";

import {
  Plus,
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
  useCreateTenant,
} from "../hooks";


export default function CreateTenantDialog() {
  const mutation =
    useCreateTenant();

  const [
    open,
    setOpen,
  ] = useState(false);

  const [
    name,
    setName,
  ] = useState("");

  const [
    slug,
    setSlug,
  ] = useState("");


  function resetForm() {
    setName("");
    setSlug("");
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

    if (
      !name.trim() ||
      !slug.trim()
    ) {
      return;
    }

    try {
      await mutation.mutateAsync({
        name:
          name.trim(),

        slug:
          slug
            .trim()
            .toLowerCase(),
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
        <Plus className="mr-2 h-4 w-4" />

        Create Tenant
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
              Create Tenant
            </DialogTitle>

            <DialogDescription>
              Create a new tenant
              organization.
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
                Tenant Name
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
                placeholder="Acme Corporation"
                className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm outline-none focus:border-blue-500"
                required
              />
            </div>


            <div>
              <label className="text-sm font-medium text-slate-700">
                Slug
              </label>

              <input
                value={
                  slug
                }
                onChange={(
                  event,
                ) =>
                  setSlug(
                    event.target.value,
                  )
                }
                placeholder="acme"
                className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm outline-none focus:border-blue-500"
                required
              />

              <p className="mt-1 text-xs text-slate-400">
                Slug will be saved
                in lowercase.
              </p>
            </div>


            {mutation.isError && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                Failed to create tenant.
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
                  !name.trim() ||
                  !slug.trim()
                }
              >
                {
                  mutation.isPending
                    ? "Creating..."
                    : "Create Tenant"
                }
              </Button>

            </DialogFooter>

          </form>

        </DialogContent>
      </Dialog>
    </>
  );
}