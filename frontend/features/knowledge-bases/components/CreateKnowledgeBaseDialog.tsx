"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import {
  knowledgeBaseSchema,
  type KnowledgeBaseForm,
} from "../schemas";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

type Props = {
  onCreate: (
    values: KnowledgeBaseForm,
  ) => Promise<void>;
};

export default function CreateKnowledgeBaseDialog({
  onCreate,
}: Props) {
  const [open, setOpen] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: {
      errors,
      isSubmitting,
    },
  } = useForm<KnowledgeBaseForm>({
    resolver: zodResolver(
      knowledgeBaseSchema,
    ),
    defaultValues: {
      name: "",
      description: "",
      visibility: "PRIVATE",
    },
  });

  async function submit(
    values: KnowledgeBaseForm,
  ) {
    console.log(
      "Submitting KB:",
      values,
    );

    await onCreate(values);

    reset({
      name: "",
      description: "",
      visibility: "PRIVATE",
    });

    setOpen(false);
  }

  function onInvalid(errors: unknown) {
    console.log(
      "Validation errors:",
      errors,
    );
  }

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="rounded-lg bg-blue-600 px-5 py-2 text-white hover:bg-blue-700"
      >
        + Create Knowledge Base
      </button>

      <Dialog
        open={open}
        onOpenChange={setOpen}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              Create Knowledge Base
            </DialogTitle>
          </DialogHeader>

          <form
            onSubmit={handleSubmit(
              submit,
              onInvalid,
            )}
            className="space-y-5"
          >
            <input
              type="hidden"
              {...register("visibility")}
            />

            <div>
              <Label htmlFor="name">
                Name
              </Label>

              <Input
                id="name"
                {...register("name")}
              />

              {errors.name && (
                <p className="mt-1 text-sm text-red-500">
                  {errors.name.message}
                </p>
              )}
            </div>

            <div>
              <Label htmlFor="description">
                Description
              </Label>

              <Textarea
                id="description"
                rows={4}
                {...register(
                  "description",
                )}
              />

              {errors.description && (
                <p className="mt-1 text-sm text-red-500">
                  {
                    errors.description
                      .message
                  }
                </p>
              )}
            </div>

            <DialogFooter>
              <button
                type="submit"
                disabled={isSubmitting}
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