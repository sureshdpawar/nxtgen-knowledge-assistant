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
  useDeleteLLMProfile,
} from "../hooks";

import type {
  LLMProfile,
} from "../types";


type Props = {
  profile: LLMProfile;
};


export default function DeleteLLMProfileDialog({
  profile,
}: Props) {
  const mutation =
    useDeleteLLMProfile();

  const [
    open,
    setOpen,
  ] = useState(false);


  async function confirmDelete() {
    try {
      await mutation.mutateAsync(
        profile.id,
      );

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
        disabled={
          profile.is_default
        }
        className="border-red-200 text-red-600 hover:bg-red-50 hover:text-red-700"
      >
        <Trash2 className="mr-2 h-4 w-4" />

        Delete
      </Button>


      <Dialog
        open={
          open
        }
        onOpenChange={
          setOpen
        }
      >
        <DialogContent className="sm:max-w-md">

          <DialogHeader>

            <DialogTitle>
              Delete LLM Profile
            </DialogTitle>

            <DialogDescription>
              Are you sure you want
              to delete{" "}
              <span className="font-medium text-slate-700">
                {
                  profile.name
                }
              </span>
              ?
            </DialogDescription>

          </DialogHeader>


          <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
            Any knowledge bases using
            this profile will fall back
            to the tenant default
            profile.
          </div>


          {mutation.isError && (
            <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              Failed to delete LLM
              profile.
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
              type="button"
              disabled={
                mutation.isPending
              }
              onClick={
                confirmDelete
              }
              className="bg-red-600 text-white hover:bg-red-700"
            >
              <Trash2 className="mr-2 h-4 w-4" />

              {
                mutation.isPending
                  ? "Deleting..."
                  : "Delete Profile"
              }
            </Button>

          </DialogFooter>

        </DialogContent>
      </Dialog>
    </>
  );
}