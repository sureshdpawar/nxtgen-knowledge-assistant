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

import {
  Input,
} from "@/components/ui/input";

import {
  Label,
} from "@/components/ui/label";


type Props = {
  onCreate: (
    payload:
      CreateKnowledgeSourceRequest,
  ) => Promise<void>;
};


export default function CreateKnowledgeSourceDialog({
  onCreate,
}: Props) {
  const [
    open,
    setOpen,
  ] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    watch,
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
      baseUrl: "",
      maxPages: 25,
      maxDepth: 2,
    },
  });

  const sourceType =
    watch("type");

  async function submit(
    values:
      KnowledgeSourceForm,
  ) {
    let configuration:
      Record<string, unknown>
      = {};

    if (
      values.type
      === "WEBSITE"
    ) {
      configuration = {
        base_url:
          values.baseUrl
            ?.trim(),

        max_pages:
          values.maxPages,

        max_depth:
          values.maxDepth,

        include_patterns: [],

        exclude_patterns: [],
      };
    }

    const payload:
      CreateKnowledgeSourceRequest = {
        name:
          values.name.trim(),

        type:
          values.type,

        configuration,
      };

    await onCreate(
      payload,
    );

    reset({
      name: "",
      type: "UPLOAD",
      baseUrl: "",
      maxPages: 25,
      maxDepth: 2,
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
            onSubmit={
              handleSubmit(
                submit,
              )
            }
            className="space-y-5"
          >
            <div>
              <Label
                htmlFor="source-name"
              >
                Name
              </Label>

              <Input
                id="source-name"
                placeholder={
                  sourceType
                  === "WEBSITE"
                    ? "Example: Company Website"
                    : "Example: Engineering Uploads"
                }
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
                htmlFor="source-type"
              >
                Source Type
              </Label>

              <select
                id="source-type"
                {...register(
                  "type",
                )}
                className="mt-2 flex h-10 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 outline-none focus:border-blue-500"
              >
                <option
                  value="UPLOAD"
                >
                  File Upload
                </option>

                <option
                  value="WEBSITE"
                >
                  Website
                </option>
              </select>
            </div>

            {sourceType
              === "WEBSITE"
              && (
                <>
                  <div>
                    <Label
                      htmlFor="source-base-url"
                    >
                      Website URL
                    </Label>

                    <Input
                      id="source-base-url"
                      placeholder="https://example.com"
                      {...register(
                        "baseUrl",
                      )}
                    />

                    {errors.baseUrl
                      && (
                        <p className="mt-1 text-sm text-red-500">
                          {
                            errors
                              .baseUrl
                              .message
                          }
                        </p>
                      )}

                    <p className="mt-1 text-xs text-slate-500">
                      The crawler will stay
                      on the same hostname.
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label
                        htmlFor="source-max-pages"
                      >
                        Max Pages
                      </Label>

                      <Input
                        id="source-max-pages"
                        type="number"
                        min={1}
                        max={200}
                        {...register(
                          "maxPages",
                          {
                            valueAsNumber:
                              true,
                          },
                        )}
                      />
                    </div>

                    <div>
                      <Label
                        htmlFor="source-max-depth"
                      >
                        Max Depth
                      </Label>

                      <Input
                        id="source-max-depth"
                        type="number"
                        min={0}
                        max={10}
                        {...register(
                          "maxDepth",
                          {
                            valueAsNumber:
                              true,
                          },
                        )}
                      />
                    </div>
                  </div>

                  <div className="rounded-lg bg-slate-50 p-3 text-xs text-slate-600">
                    Website sync is manual.
                    Creating this source does
                    not crawl the site yet.
                    After creation, use
                    <strong>
                      {" "}Sync Now
                    </strong>
                    .
                  </div>
                </>
              )}

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