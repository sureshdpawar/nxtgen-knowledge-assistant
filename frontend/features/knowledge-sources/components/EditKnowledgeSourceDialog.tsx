"use client";

import { useEffect } from "react";
import { useForm } from "react-hook-form";

import type {
  KnowledgeSource,
  UpdateKnowledgeSourceRequest,
} from "../types";

import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";


type Props = {
  knowledgeSource:
    KnowledgeSource | null;

  open: boolean;

  onOpenChange:
    (open: boolean) => void;

  onUpdate: (
    id: string,
    payload:
      UpdateKnowledgeSourceRequest,
  ) => Promise<void>;
};


type EditKnowledgeSourceForm = {
  name: string;
  status: "ACTIVE";
};


export default function EditKnowledgeSourceDialog({
  knowledgeSource,
  open,
  onOpenChange,
  onUpdate,
}: Props) {
  const {
    register,
    handleSubmit,
    reset,
    formState: {
      errors,
      isSubmitting,
    },
  } =
    useForm<EditKnowledgeSourceForm>({
      defaultValues: {
        name: "",
        status: "ACTIVE",
      },
    });


  useEffect(() => {
    if (!knowledgeSource) {
      return;
    }

    reset({
      name:
        knowledgeSource.name,

      status:
        knowledgeSource.status,
    });
  }, [
    knowledgeSource,
    reset,
  ]);


  async function submit(
    values:
      EditKnowledgeSourceForm,
  ) {
    if (!knowledgeSource) {
      return;
    }

    const payload:
      UpdateKnowledgeSourceRequest =
      {
        name:
          values.name,

        status:
          values.status,

        configuration:
          knowledgeSource.configuration
          ?? {},
      };

    await onUpdate(
      knowledgeSource.id,
      payload,
    );

    onOpenChange(false);
  }


  return (
    <Dialog
      open={open}
      onOpenChange={
        onOpenChange
      }
    >
      <DialogContent>

        <DialogHeader>
          <DialogTitle>
            Edit Knowledge Source
          </DialogTitle>
        </DialogHeader>

        <form
          onSubmit={
            handleSubmit(
              submit,
            )
          }
          className="space-y-5"
        >

          <div>
            <Label
              htmlFor="edit-source-name"
            >
              Name
            </Label>

            <Input
              id="edit-source-name"
              {...register(
                "name",
                {
                  required:
                    "Name is required",
                  minLength: {
                    value: 2,
                    message:
                      "Minimum 2 characters",
                  },
                },
              )}
            />

            {errors.name && (
              <p className="mt-1 text-sm text-red-500">
                {
                  errors.name
                    .message
                }
              </p>
            )}
          </div>


          <div>
            <Label>
              Source Type
            </Label>

            <Input
              value={
                knowledgeSource
                  ?.type
                ?? "UPLOAD"
              }
              disabled
            />
          </div>


          <div>
            <Label>
              Status
            </Label>

            <Input
              value="ACTIVE"
              disabled
            />

            <input
              type="hidden"
              {...register(
                "status",
              )}
            />
          </div>


          <DialogFooter>
            <button
              type="submit"
              disabled={
                isSubmitting
              }
              className="rounded-lg bg-blue-600 px-5 py-2 text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isSubmitting
                ? "Saving..."
                : "Save Changes"}
            </button>
          </DialogFooter>

        </form>

      </DialogContent>
    </Dialog>
  );
}