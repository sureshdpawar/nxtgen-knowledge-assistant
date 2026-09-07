"use client";

import {
  useEffect,
} from "react";

import {
  useForm,
} from "react-hook-form";

import type {
  KnowledgeSource,
  KnowledgeSourceStatus,
  UpdateKnowledgeSourceRequest,
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

  status:
    KnowledgeSourceStatus;

  baseUrl: string;

  maxPages: number;

  maxDepth: number;

  driveFolderUrl: string;

  driveRecursive: boolean;
};


function stringValue(
  configuration: Record<string, unknown>,
  key: string,
  fallback = "",
): string {
  const value = configuration[key];

  return typeof value === "string"
    ? value
    : fallback;
}


function numberValue(
  configuration: Record<string, unknown>,
  key: string,
  fallback: number,
): number {
  const value = configuration[key];

  return typeof value === "number"
    && Number.isFinite(value)
    ? value
    : fallback;
}


function booleanValue(
  configuration: Record<string, unknown>,
  key: string,
  fallback: boolean,
): boolean {
  const value = configuration[key];

  return typeof value === "boolean"
    ? value
    : fallback;
}


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
        baseUrl: "",
        maxPages: 500,
        maxDepth: 2,
        driveFolderUrl: "",
        driveRecursive: true,
      },
    });


  useEffect(() => {
    if (!knowledgeSource) {
      return;
    }

    const configuration =
      knowledgeSource.configuration
      ?? {};

    reset({
      name:
        knowledgeSource.name,

      status:
        knowledgeSource.status,

      baseUrl:
        stringValue(
          configuration,
          "base_url",
        ),

      maxPages:
        numberValue(
          configuration,
          "max_pages",
          500,
        ),

      maxDepth:
        numberValue(
          configuration,
          "max_depth",
          2,
        ),

      driveFolderUrl:
        stringValue(
          configuration,
          "folder_url",
        ),

      driveRecursive:
        booleanValue(
          configuration,
          "recursive",
          true,
        ),
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

    const existingConfiguration = {
      ...(
        knowledgeSource.configuration
        ?? {}
      ),
    };

    let configuration:
      Record<string, unknown> =
      existingConfiguration;

    if (
      knowledgeSource.type
      === "WEBSITE"
    ) {
      configuration = {
        ...existingConfiguration,

        base_url:
          values.baseUrl.trim(),

        max_pages:
          values.maxPages,

        max_depth:
          values.maxDepth,
      };
    }

    if (
      knowledgeSource.type
      === "GOOGLE_DRIVE"
    ) {
      configuration = {
        ...existingConfiguration,

        folder_url:
          values
            .driveFolderUrl
            .trim(),

        recursive:
          values
            .driveRecursive,
      };
    }

    const payload:
      UpdateKnowledgeSourceRequest =
      {
        name:
          values.name.trim(),

        status:
          values.status,

        configuration,
      };

    await onUpdate(
      knowledgeSource.id,
      payload,
    );

    onOpenChange(
      false,
    );
  }


  return (
    <Dialog
      open={
        open
      }
      onOpenChange={
        onOpenChange
      }
    >
      <DialogContent className="max-h-[90vh] overflow-y-auto">

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
              value={
                knowledgeSource
                  ?.status
                ?? "ACTIVE"
              }
              disabled
            />

            <input
              type="hidden"
              {...register(
                "status",
              )}
            />
          </div>


          {knowledgeSource
            ?.type === "WEBSITE"
            && (
              <>
                <div>
                  <Label
                    htmlFor="edit-source-base-url"
                  >
                    Website URL
                  </Label>

                  <Input
                    id="edit-source-base-url"
                    placeholder="https://example.com"
                    {...register(
                      "baseUrl",
                      {
                        required:
                          "Website URL is required",
                      },
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
                      htmlFor="edit-source-max-pages"
                    >
                      Max Pages
                    </Label>

                    <Input
                      id="edit-source-max-pages"
                      type="number"
                      min={1}
                      max={500}
                      {...register(
                        "maxPages",
                        {
                          valueAsNumber: true,
                          required:
                            "Max pages is required",
                          min: {
                            value: 1,
                            message:
                              "Minimum is 1",
                          },
                          max: {
                            value: 500,
                            message:
                              "Maximum is 500",
                          },
                        },
                      )}
                    />

                    {errors.maxPages
                      && (
                        <p className="mt-1 text-sm text-red-500">
                          {
                            errors
                              .maxPages
                              .message
                          }
                        </p>
                      )}
                  </div>


                  <div>
                    <Label
                      htmlFor="edit-source-max-depth"
                    >
                      Max Depth
                    </Label>

                    <Input
                      id="edit-source-max-depth"
                      type="number"
                      min={0}
                      max={10}
                      {...register(
                        "maxDepth",
                        {
                          valueAsNumber: true,
                          required:
                            "Max depth is required",
                          min: {
                            value: 0,
                            message:
                              "Minimum is 0",
                          },
                          max: {
                            value: 10,
                            message:
                              "Maximum is 10",
                          },
                        },
                      )}
                    />

                    {errors.maxDepth
                      && (
                        <p className="mt-1 text-sm text-red-500">
                          {
                            errors
                              .maxDepth
                              .message
                          }
                        </p>
                      )}
                  </div>

                </div>


                <div className="rounded-lg bg-slate-50 p-3 text-xs text-slate-600">
                  Changes apply to the next
                  manual website sync.
                  Existing stored crawler
                  configuration is preserved
                  unless changed here.
                </div>
              </>
            )}


          {knowledgeSource
            ?.type === "GOOGLE_DRIVE"
            && (
              <>
                <div>
                  <Label
                    htmlFor="edit-drive-folder-url"
                  >
                    Google Drive Folder
                  </Label>

                  <Input
                    id="edit-drive-folder-url"
                    placeholder="https://drive.google.com/drive/folders/..."
                    {...register(
                      "driveFolderUrl",
                      {
                        required:
                          "Google Drive folder is required",
                      },
                    )}
                  />

                  {errors.driveFolderUrl
                    && (
                      <p className="mt-1 text-sm text-red-500">
                        {
                          errors
                            .driveFolderUrl
                            .message
                        }
                      </p>
                    )}
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
              </>
            )}


          <DialogFooter>

            <button
              type="submit"
              disabled={
                isSubmitting
              }
              className="rounded-lg bg-blue-600 px-5 py-2 text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {
                isSubmitting
                  ? "Saving..."
                  : "Save Changes"
              }
            </button>

          </DialogFooter>

        </form>

      </DialogContent>
    </Dialog>
  );
}
