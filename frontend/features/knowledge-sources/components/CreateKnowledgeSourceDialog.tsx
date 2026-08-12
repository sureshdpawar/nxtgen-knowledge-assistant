"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import {
  knowledgeSourceSchema,
  type KnowledgeSourceForm,
} from "../schemas";

import type {
  CreateKnowledgeSourceRequest,
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
  onCreate: (
    payload: CreateKnowledgeSourceRequest,
  ) => Promise<void>;
};

export default function CreateKnowledgeSourceDialog({
  onCreate,
}: Props) {
  const [open, setOpen] =
    useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: {
      errors,
      isSubmitting,
    },
  } = useForm<KnowledgeSourceForm>({
    resolver: zodResolver(
      knowledgeSourceSchema,
    ),

    defaultValues: {
      name: "",
      type: "UPLOAD",
    },
  });

  async function submit(
    values: KnowledgeSourceForm,
  ) {
    const payload:
      CreateKnowledgeSourceRequest = {
        name: values.name,
        type: values.type,
        configuration: {},
      };

    await onCreate(payload);

    reset({
      name: "",
      type: "UPLOAD",
    });

    setOpen(false);
  }

  return (
    <>
      <button
        type="button"
        onClick={() =>
          setOpen(true)
        }
        className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
      >
        + Create Knowledge Source
      </button>

      <Dialog
        open={open}
        onOpenChange={
          setOpen
        }
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              Create Knowledge Source
            </DialogTitle>
          </DialogHeader>

          <form
            onSubmit={handleSubmit(
              submit,
            )}
            className="space-y-5"
          >
            <input
              type="hidden"
              {...register("type")}
            />

            <div>
              <Label
                htmlFor="source-name"
              >
                Name
              </Label>

              <Input
                id="source-name"
                placeholder="Example: Engineering Uploads"
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
              <Label>
                Source Type
              </Label>

              <Input
                value="UPLOAD"
                disabled
              />

              <p className="mt-1 text-xs text-slate-500">
                Additional source
                types can be added
                later.
              </p>
            </div>

            <DialogFooter>
              <button
                type="submit"
                disabled={
                  isSubmitting
                }
                className="rounded-lg bg-blue-600 px-5 py-2 text-white disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isSubmitting
                  ? "Creating..."
                  : "Create"}
              </button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </>
  );
}