"use client";

import {
  useState,
} from "react";

import {
  Trash2,
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
  useDeleteIntegration,
} from "../hooks";

import type {
  Integration,
} from "../types";


type Props = {
  integration: Integration;
};


export default function DeleteIntegrationDialog({
  integration,
}: Props) {
  const [
    open,
    setOpen,
  ] = useState(false);

  const mutation =
    useDeleteIntegration();


  async function handleDelete() {
    try {
      await mutation.mutateAsync(
        integration.id,
      );

      setOpen(false);

    } catch {
      // Error rendered below.
    }
  }


  return (
    <>
      <Button
        type="button"
        size="sm"
        variant="outline"
        onClick={() =>
          setOpen(true)
        }
        disabled={
          mutation.isPending
        }
      >
        <Trash2 className="mr-2 h-4 w-4" />

        Delete
      </Button>


      <Dialog
        open={open}
        onOpenChange={
          setOpen
        }
      >
        <DialogContent className="sm:max-w-md">

          <DialogHeader>

            <DialogTitle>
              Delete Integration?
            </DialogTitle>

            <DialogDescription>
              You are about to permanently
              remove{" "}
              <span className="font-medium text-slate-700">
                {integration.name}
              </span>
              .
            </DialogDescription>

          </DialogHeader>


          <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">

            <p className="text-sm font-medium text-amber-800">
              This action cannot be undone.
            </p>

            <p className="mt-1 text-sm text-amber-700">
              Tools associated with this
              integration may also be
              removed or become unavailable
              to agents.
            </p>

          </div>


          <div className="rounded-lg border bg-slate-50 p-4">

            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Integration
            </p>

            <p className="mt-1 text-sm font-semibold text-slate-800">
              {integration.name}
            </p>


            <p className="mt-3 text-xs font-medium uppercase tracking-wide text-slate-400">
              Type
            </p>

            <p className="mt-1 text-sm text-slate-700">
              {integration.integration_type}
            </p>


            <p className="mt-3 text-xs font-medium uppercase tracking-wide text-slate-400">
              Endpoint
            </p>

            <p className="mt-1 break-all font-mono text-xs text-slate-600">
              {integration.base_url}
            </p>

          </div>


          {mutation.isError && (
            <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              Failed to delete integration.
            </div>
          )}


          <DialogFooter>

            <Button
              type="button"
              variant="outline"
              onClick={() =>
                setOpen(false)
              }
              disabled={
                mutation.isPending
              }
            >
              Cancel
            </Button>


            <Button
              type="button"
              onClick={
                handleDelete
              }
              disabled={
                mutation.isPending
              }
              className="bg-red-600 text-white hover:bg-red-700"
            >
              <Trash2 className="mr-2 h-4 w-4" />

              {mutation.isPending
                ? "Deleting..."
                : "Delete Integration"}
            </Button>

          </DialogFooter>

        </DialogContent>
      </Dialog>
    </>
  );
}