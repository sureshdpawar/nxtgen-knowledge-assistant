"use client";

import {
  useEffect,
} from "react";

import {
  useForm,
} from "react-hook-form";

import {
  zodResolver,
} from "@hookform/resolvers/zod";

import {
  knowledgeBaseSchema,
  type KnowledgeBaseForm,
} from "../schemas";

import type {
  KnowledgeBase,
} from "../types";

import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import {
  Input,
} from "@/components/ui/input";

import {
  Label,
} from "@/components/ui/label";

import {
  Textarea,
} from "@/components/ui/textarea";


type Props = {
  knowledgeBase:
    KnowledgeBase | null;

  open: boolean;

  onOpenChange:
    (open: boolean) => void;

  onUpdate: (
    id: string,
    values:
      KnowledgeBaseForm,
  ) => Promise<void>;
};


export default function EditKnowledgeBaseDialog({
  knowledgeBase,
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
    useForm<KnowledgeBaseForm>({
      resolver:
        zodResolver(
          knowledgeBaseSchema,
        ),
    });


  useEffect(() => {
    if (!knowledgeBase) {
      return;
    }

    reset({
      name:
        knowledgeBase.name,

      description:
        knowledgeBase.description
        ?? "",

      visibility:
        knowledgeBase.visibility,
    });

  }, [
    knowledgeBase,
    reset,
  ]);


  async function submit(
    values:
      KnowledgeBaseForm,
  ) {
    if (!knowledgeBase) {
      return;
    }

    await onUpdate(
      knowledgeBase.id,
      values,
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
            Edit Knowledge Base
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

          <input
            type="hidden"
            {...register(
              "visibility",
            )}
          />

          <div>
            <Label
              htmlFor="edit-name"
            >
              Name
            </Label>

            <Input
              id="edit-name"
              {...register(
                "name",
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
            <Label
              htmlFor="edit-description"
            >
              Description
            </Label>

            <Textarea
              id="edit-description"
              rows={4}
              {...register(
                "description",
              )}
            />

            {errors.description && (
              <p className="mt-1 text-sm text-red-500">
                {
                  errors
                    .description
                    .message
                }
              </p>
            )}
          </div>

          <DialogFooter>
            <button
              type="submit"
              disabled={
                isSubmitting
              }
              className="rounded-lg bg-blue-600 px-5 py-2 text-white disabled:opacity-50"
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