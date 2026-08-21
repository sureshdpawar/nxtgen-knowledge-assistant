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
  ] =
    useState(false);

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

      driveFolderUrl: "",
      driveRecursive: true,
    },

  });


  const sourceType =
    watch(
      "type",
    );


  async function submit(
    values:
      KnowledgeSourceForm,
  ) {
    let configuration:
      Record<string, unknown>
      = {};


    /*
     * Website
     */
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


    /*
     * Google Drive
     */
    if (
      values.type
      === "GOOGLE_DRIVE"
    ) {

      configuration = {

        folder_url:
          values
            .driveFolderUrl
            ?.trim(),

        recursive:
          values
            .driveRecursive,

      };
    }


    const payload:
      CreateKnowledgeSourceRequest = {

        name:
          values
            .name
            .trim(),

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

      driveFolderUrl: "",
      driveRecursive: true,

    });


    setOpen(
      false,
    );
  }


  function getNamePlaceholder() {

    if (
      sourceType
      === "WEBSITE"
    ) {
      return (
        "Example: Company Website"
      );
    }

    if (
      sourceType
      === "GOOGLE_DRIVE"
    ) {
      return (
        "Example: Finance Drive"
      );
    }

    return (
      "Example: Engineering Uploads"
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
        className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
      >
        + Create Knowledge Source
      </button>


      <Dialog
        open={
          open
        }
        onOpenChange={
          setOpen
        }
      >

        <DialogContent className="max-h-[90vh] overflow-y-auto">

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

            {/* Name */}
            <div>

              <Label
                htmlFor="source-name"
              >
                Name
              </Label>

              <Input
                id="source-name"
                placeholder={
                  getNamePlaceholder()
                }
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


            {/* Source type */}
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

                <option
                  value="GOOGLE_DRIVE"
                >
                  Google Drive
                </option>

              </select>

            </div>


            {/* Website */}
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
                      The crawler stays on
                      the same hostname.
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
                        min={
                          1
                        }
                        max={
                          200
                        }
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
                        min={
                          0
                        }
                        max={
                          10
                        }
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
                    After creating the source,
                    use{" "}
                    <strong>
                      Sync Now
                    </strong>
                    .
                  </div>

                </>
              )}


            {/* Google Drive */}
            {sourceType
              === "GOOGLE_DRIVE"
              && (
                <>

                  <div>

                    <Label
                      htmlFor="drive-folder-url"
                    >
                      Google Drive Folder
                    </Label>

                    <Input
                      id="drive-folder-url"
                      placeholder="https://drive.google.com/drive/folders/..."
                      {...register(
                        "driveFolderUrl",
                      )}
                    />

                    {errors
                      .driveFolderUrl
                      && (
                        <p className="mt-1 text-sm text-red-500">
                          {
                            errors
                              .driveFolderUrl
                              .message
                          }
                        </p>
                      )}

                    <p className="mt-1 text-xs text-slate-500">
                      Paste the folder URL
                      or raw Google Drive
                      folder ID.
                    </p>

                  </div>


                  <label className="flex items-start gap-3 rounded-lg border p-4">

                    <input
                      type="checkbox"
                      {...register(
                        "driveRecursive",
                      )}
                      className="mt-1 h-4 w-4"
                    />

                    <div>

                      <p className="text-sm font-medium text-slate-900">
                        Include subfolders
                      </p>

                      <p className="mt-1 text-xs text-slate-500">
                        Discover supported
                        documents recursively
                        inside this Drive folder.
                      </p>

                    </div>

                  </label>


                  <div className="rounded-lg bg-blue-50 p-4">

                    <p className="text-sm font-medium text-blue-900">
                      Folder access
                    </p>

                    <p className="mt-2 text-xs leading-5 text-blue-800">
                      Share this Google Drive
                      folder with the NXTGEN
                      service-account email
                      using Viewer permission
                      before running the first
                      sync.
                    </p>

                  </div>


                  <div className="rounded-lg bg-slate-50 p-3 text-xs text-slate-600">
                    Creating the source does
                    not download files.
                    After creation, use{" "}
                    <strong>
                      Sync Now
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