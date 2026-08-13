"use client";

import type {
  Document,
} from "../types";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

type Props = {
  document:
    Document | null;

  open: boolean;

  onOpenChange:
    (open: boolean) => void;

  onDelete:
    (id: string) =>
      Promise<void>;

  deleting: boolean;
};

export default function DeleteDocumentDialog({
  document,
  open,
  onOpenChange,
  onDelete,
  deleting,
}: Props) {
  async function handleDelete() {
    if (!document) {
      return;
    }

    await onDelete(
      document.id,
    );

    onOpenChange(false);
  }

  return (
    <AlertDialog
      open={open}
      onOpenChange={
        onOpenChange
      }
    >
      <AlertDialogContent>

        <AlertDialogHeader>

          <AlertDialogTitle>
            Delete Document?
          </AlertDialogTitle>

          <AlertDialogDescription>
            Are you sure you want
            to delete{" "}
            <strong>
              {
                document
                  ?.original_filename
              }
            </strong>
            ? This action cannot
            be undone.
          </AlertDialogDescription>

        </AlertDialogHeader>

        <AlertDialogFooter>

          <AlertDialogCancel>
            Cancel
          </AlertDialogCancel>

          <AlertDialogAction
            onClick={
              handleDelete
            }
            disabled={
              deleting
            }
            className="bg-red-600 text-white hover:bg-red-700"
          >
            {deleting
              ? "Deleting..."
              : "Delete"}
          </AlertDialogAction>

        </AlertDialogFooter>

      </AlertDialogContent>
    </AlertDialog>
  );
}