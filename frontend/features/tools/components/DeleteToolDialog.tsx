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
  useDeleteTool,
} from "../hooks";

import type {
  ToolDefinition,
} from "../types";


type Props = {
  tool: ToolDefinition;
};


export default function DeleteToolDialog({
  tool,
}: Props) {
  const [
    open,
    setOpen,
  ] = useState(false);

  const mutation =
    useDeleteTool();


  async function handleDelete() {
    try {
      await mutation.mutateAsync(
        tool.id,
      );

      setOpen(false);

    } catch {
      // Mutation state renders error.
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
              Delete Tool?
            </DialogTitle>

            <DialogDescription>
              Permanently remove{" "}
              <span className="font-medium text-slate-700">
                {tool.name}
              </span>
              .
            </DialogDescription>

          </DialogHeader>


          <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">

            <p className="text-sm font-medium text-amber-800">
              This action cannot be undone.
            </p>

            <p className="mt-1 text-sm text-amber-700">
              Agents assigned to this
              tool will no longer be
              able to use it.
            </p>

          </div>


          {mutation.isError && (
            <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              Failed to delete tool.
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
                : "Delete Tool"}
            </Button>

          </DialogFooter>

        </DialogContent>
      </Dialog>
    </>
  );
}