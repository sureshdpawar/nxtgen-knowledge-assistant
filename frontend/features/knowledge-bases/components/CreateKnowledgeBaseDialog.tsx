"use client";

import {
  useState,
} from "react";

import {
  useForm,
} from "react-hook-form";

import {
  zodResolver,
} from "@hookform/resolvers/zod";

import {
  knowledgeBaseSchema,
  PLATFORM_DEFAULT_CHUNK_OVERLAP,
  PLATFORM_DEFAULT_CHUNK_SIZE,
  PLATFORM_DEFAULT_TOP_K,
} from "../schemas";

import type {
  KnowledgeBaseForm,
  KnowledgeBaseFormInput,
} from "../schemas";

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
  onCreate: (
    values:
      KnowledgeBaseForm,
  ) => Promise<void>;
};


export default function CreateKnowledgeBaseDialog({
  onCreate,
}: Props) {

  const [
    open,
    setOpen,
  ] = useState(
    false,
  );


  const {
    register,
    handleSubmit,
    reset,

    formState: {
      errors,
      isSubmitting,
    },

  } =
    useForm<
      KnowledgeBaseFormInput,
      unknown,
      KnowledgeBaseForm
    >({
      resolver:
        zodResolver(
          knowledgeBaseSchema,
        ),

      defaultValues: {
        name:
          "",

        description:
          "",

        visibility:
          "PRIVATE",

        chunk_size:
          null,

        chunk_overlap:
          null,

        top_k:
          null,
      },
    });


  async function submit(
    values:
      KnowledgeBaseForm,
  ) {

    await onCreate(
      values,
    );

    reset({
      name:
        "",

      description:
        "",

      visibility:
        "PRIVATE",

      chunk_size:
        null,

      chunk_overlap:
        null,

      top_k:
        null,
    });

    setOpen(
      false,
    );
  }


  return (
    <>

      <button
        type="button"
        onClick={() =>
          setOpen(
            true,
          )
        }
        className="rounded-lg bg-blue-600 px-5 py-2 text-white hover:bg-blue-700"
      >
        + Create Knowledge Base
      </button>


      <Dialog
        open={
          open
        }
        onOpenChange={
          setOpen
        }
      >

        <DialogContent className="sm:max-w-xl">

          <DialogHeader>

            <DialogTitle>
              Create Knowledge Base
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
                htmlFor="name"
              >
                Name
              </Label>

              <Input
                id="name"
                {...register(
                  "name",
                )}
              />

              {errors.name && (
                <p className="mt-1 text-sm text-red-500">
                  {
                    errors
                      .name
                      .message
                  }
                </p>
              )}

            </div>


            <div>

              <Label
                htmlFor="description"
              >
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
                    errors
                      .description
                      .message
                  }
                </p>
              )}

            </div>


            <div className="border-t pt-5">

              <h3 className="text-sm font-semibold text-slate-900">
                RAG Configuration
              </h3>

              <p className="mt-1 text-xs text-slate-500">
                Leave these fields blank
                to use the platform
                defaults.
              </p>


              <div className="mt-4 grid gap-4 sm:grid-cols-3">

                <div>

                  <Label
                    htmlFor="chunk-size"
                  >
                    Chunk Size
                  </Label>

                  <Input
                    id="chunk-size"
                    type="number"
                    min={100}
                    max={4000}
                    placeholder={
                      String(
                        PLATFORM_DEFAULT_CHUNK_SIZE,
                      )
                    }
                    {...register(
                      "chunk_size",
                    )}
                  />

                  <p className="mt-1 text-xs text-slate-500">
                    Default:{" "}
                    {
                      PLATFORM_DEFAULT_CHUNK_SIZE
                    }
                  </p>

                  {errors.chunk_size && (
                    <p className="mt-1 text-xs text-red-500">
                      {
                        errors
                          .chunk_size
                          .message
                      }
                    </p>
                  )}

                </div>


                <div>

                  <Label
                    htmlFor="chunk-overlap"
                  >
                    Chunk Overlap
                  </Label>

                  <Input
                    id="chunk-overlap"
                    type="number"
                    min={0}
                    max={1000}
                    placeholder={
                      String(
                        PLATFORM_DEFAULT_CHUNK_OVERLAP,
                      )
                    }
                    {...register(
                      "chunk_overlap",
                    )}
                  />

                  <p className="mt-1 text-xs text-slate-500">
                    Default:{" "}
                    {
                      PLATFORM_DEFAULT_CHUNK_OVERLAP
                    }
                  </p>

                  {errors.chunk_overlap && (
                    <p className="mt-1 text-xs text-red-500">
                      {
                        errors
                          .chunk_overlap
                          .message
                      }
                    </p>
                  )}

                </div>


                <div>

                  <Label
                    htmlFor="top-k"
                  >
                    Top K
                  </Label>

                  <Input
                    id="top-k"
                    type="number"
                    min={1}
                    max={20}
                    placeholder={
                      String(
                        PLATFORM_DEFAULT_TOP_K,
                      )
                    }
                    {...register(
                      "top_k",
                    )}
                  />

                  <p className="mt-1 text-xs text-slate-500">
                    Default:{" "}
                    {
                      PLATFORM_DEFAULT_TOP_K
                    }
                  </p>

                  {errors.top_k && (
                    <p className="mt-1 text-xs text-red-500">
                      {
                        errors
                          .top_k
                          .message
                      }
                    </p>
                  )}

                </div>

              </div>


              <div className="mt-4 rounded-lg border border-blue-100 bg-blue-50 p-3 text-xs text-blue-700">

                Chunk size and overlap
                affect document ingestion.

                {" "}

                Top K controls how many
                relevant chunks are
                retrieved during search.

              </div>

            </div>


            <DialogFooter>

              <button
                type="submit"
                disabled={
                  isSubmitting
                }
                className="rounded-lg bg-blue-600 px-5 py-2 text-white disabled:cursor-not-allowed disabled:opacity-50"
              >

                {
                  isSubmitting
                    ? "Creating..."
                    : "Create"
                }

              </button>

            </DialogFooter>

          </form>

        </DialogContent>

      </Dialog>

    </>
  );
}