"use client";

import type {
  KnowledgeSource,
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
  knowledgeSource:
    KnowledgeSource | null;

  open: boolean;

  onOpenChange:
    (open: boolean) => void;

  onDelete:
    (id: string) => Promise<void>;

  deleting: boolean;
};

export default function DeleteKnowledgeSourceDialog({
  knowledgeSource,
  open,
  onOpenChange,
  onDelete,
  deleting,
}: Props) {
  async function handleDelete() {
    if (!knowledgeSource) {
      return;
    }

    await onDelete(
      knowledgeSource.id,
    );

    onOpenChange(false);
  }

  return (
    <AlertDialog
      open={open}
      onOpenChange={onOpenChange}
    >
      <AlertDialogContent>

        <AlertDialogHeader>

          <AlertDialogTitle>
            Delete Knowledge Source?
          </AlertDialogTitle>

          <AlertDialogDescription>
            Are you sure you want to
            delete{" "}
            <strong>
              {knowledgeSource?.name}
            </strong>
            ? This action cannot be
            undone.
          </AlertDialogDescription>

        </AlertDialogHeader>

        <AlertDialogFooter>

          <AlertDialogCancel>
            Cancel
          </AlertDialogCancel>

          <AlertDialogAction
            onClick={handleDelete}
            disabled={deleting}
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