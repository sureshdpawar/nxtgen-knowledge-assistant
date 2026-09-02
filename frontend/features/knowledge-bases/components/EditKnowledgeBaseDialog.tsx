"use client";

import {
  useEffect,
  useState,
} from "react";

import {
  Controller,
  useForm,
} from "react-hook-form";

import {
  zodResolver,
} from "@hookform/resolvers/zod";

import {
  knowledgeBaseSchema,
  PLATFORM_DEFAULT_CHUNK_OVERLAP,
  PLATFORM_DEFAULT_CHUNK_SIZE,
  PLATFORM_DEFAULT_RERANKING_ENABLED,
  PLATFORM_DEFAULT_TOP_K,
} from "../schemas";

import type {
  KnowledgeBaseForm,
  KnowledgeBaseFormInput,
} from "../schemas";

import type {
  KnowledgeBase,
} from "../types";

import {
  useUpdateKnowledgeBaseLLMProfile,
} from "../hooks";

import {
  useLLMProfiles,
} from "@/features/llm-config/hooks";

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
    control,
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
    });


  const {
    data:
      llmProfiles,

    isLoading:
      profilesLoading,

    error:
      profilesError,
  } =
    useLLMProfiles(
      open,
    );


  const llmProfileMutation =
    useUpdateKnowledgeBaseLLMProfile();


  const [
    selectedProfileId,
    setSelectedProfileId,
  ] = useState("");


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

      chunk_size:
        knowledgeBase.chunk_size,

      chunk_overlap:
        knowledgeBase.chunk_overlap,

      top_k:
        knowledgeBase.top_k,

      reranking_enabled:
        knowledgeBase
          .reranking_enabled,
    });

    setSelectedProfileId(
      knowledgeBase
        .llm_configuration_id
        ?? "",
    );

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

    try {
      await onUpdate(
        knowledgeBase.id,
        values,
      );


      await (
        llmProfileMutation
        .mutateAsync({
          knowledgeBaseId:
            knowledgeBase.id,

          data: {
            llm_configuration_id:
              selectedProfileId ||
              null,
          },
        })
      );


      onOpenChange(
        false,
      );

    } catch {
      //
      // Errors are handled by
      // the mutation / parent UI.
      //
    }
  }


  const activeProfiles =
    (
      llmProfiles ?? []
    ).filter(
      (
        profile,
      ) =>
        profile.is_active,
    );


  const defaultProfile =
    (
      llmProfiles ?? []
    ).find(
      (
        profile,
      ) =>
        profile.is_default,
    );


  const saving =
    isSubmitting ||
    llmProfileMutation.isPending;


  return (
    <Dialog
      open={
        open
      }
      onOpenChange={
        onOpenChange
      }
    >

      <DialogContent className="sm:max-w-2xl">

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
                  errors
                    .name
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


          <div className="border-t pt-5">

            <h3 className="text-sm font-semibold text-slate-900">
              RAG Configuration
            </h3>

            <p className="mt-1 text-xs text-slate-500">
              Leave an override at its
              platform default unless this
              knowledge base needs
              different retrieval behavior.
            </p>


            <div className="mt-4 grid gap-4 sm:grid-cols-3">

              <div>

                <Label
                  htmlFor="edit-chunk-size"
                >
                  Chunk Size
                </Label>

                <Input
                  id="edit-chunk-size"
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
                  Platform default:{" "}
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
                  htmlFor="edit-chunk-overlap"
                >
                  Chunk Overlap
                </Label>

                <Input
                  id="edit-chunk-overlap"
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
                  Platform default:{" "}
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
                  htmlFor="edit-top-k"
                >
                  Top K
                </Label>

                <Input
                  id="edit-top-k"
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
                  Platform default:{" "}
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


            <div className="mt-4">

              <Label
                htmlFor="edit-reranking-enabled"
              >
                Reranking
              </Label>

              <Controller
                control={
                  control
                }
                name="reranking_enabled"
                render={({
                  field,
                }) => (
                  <select
                    id="edit-reranking-enabled"
                    value={
                      field.value === null
                        ? ""
                        : field.value
                          ? "true"
                          : "false"
                    }
                    onChange={(
                      event,
                    ) => {
                      const value =
                        event.target.value;

                      field.onChange(
                        value === ""
                          ? null
                          : value === "true",
                      );
                    }}
                    onBlur={
                      field.onBlur
                    }
                    ref={
                      field.ref
                    }
                    className="mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm outline-none focus:border-blue-500"
                  >
                    <option value="">
                      Use Platform Default
                      {" "}
                      (
                      {
                        PLATFORM_DEFAULT_RERANKING_ENABLED
                          ? "Enabled"
                          : "Disabled"
                      }
                      )
                    </option>

                    <option value="true">
                      Enabled
                    </option>

                    <option value="false">
                      Disabled
                    </option>
                  </select>
                )}
              />

              <p className="mt-1 text-xs text-slate-500">
                Reranking may improve
                retrieval quality, but
                increases latency and
                compute. The platform
                default is currently
                disabled.
              </p>

            </div>


            <div className="mt-4 rounded-lg border border-amber-100 bg-amber-50 p-3 text-xs text-amber-800">

              Top K and reranking changes
              take effect immediately.

              {" "}

              Changing Chunk Size or
              Chunk Overlap affects new
              document processing.

              {" "}

              Existing documents must be
              reprocessed for those
              chunking changes to apply.

            </div>

          </div>


          <div className="border-t pt-5">

            <Label
              htmlFor="edit-llm-profile"
            >
              LLM Profile
            </Label>


            <p className="mt-1 text-xs text-slate-500">
              Choose which LLM profile
              this knowledge base should
              use for Chat.
            </p>


            {profilesLoading ? (
              <p className="mt-3 text-sm text-slate-500">
                Loading LLM profiles...
              </p>
            ) : (
              <select
                id="edit-llm-profile"
                value={
                  selectedProfileId
                }
                onChange={(
                  event,
                ) =>
                  setSelectedProfileId(
                    event.target.value,
                  )
                }
                className="mt-3 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm outline-none focus:border-blue-500"
              >

                <option value="">
                  Use Tenant Default
                  {
                    defaultProfile
                      ? ` (${defaultProfile.name} • ${defaultProfile.model_name})`
                      : ""
                  }
                </option>


                {activeProfiles.map(
                  (
                    profile,
                  ) => (
                    <option
                      key={
                        profile.id
                      }
                      value={
                        profile.id
                      }
                    >
                      {
                        profile.name
                      }

                      {" • "}

                      {
                        profile
                          .model_name
                      }

                      {
                        profile
                          .is_default
                          ? " (Default)"
                          : ""
                      }

                    </option>
                  ),
                )}

              </select>
            )}


            {selectedProfileId === "" &&
              defaultProfile && (
              <div className="mt-3 rounded-lg border border-blue-100 bg-blue-50 p-3 text-xs text-blue-700">

                This knowledge base will
                inherit{" "}

                <span className="font-semibold">
                  {
                    defaultProfile
                      .name
                  }
                </span>

                {" "}using{" "}

                <span className="font-semibold">
                  {
                    defaultProfile
                      .model_name
                  }
                </span>
                .

              </div>
            )}


            {profilesError && (
              <div className="mt-3 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                Failed to load LLM
                profiles.
              </div>
            )}

          </div>


          {llmProfileMutation.isError && (
            <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              Failed to update the LLM
              profile for this knowledge
              base.
            </div>
          )}


          <DialogFooter>

            <button
              type="button"
              disabled={
                saving
              }
              onClick={() =>
                onOpenChange(
                  false,
                )
              }
              className="rounded-lg border border-slate-200 px-5 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
            >
              Cancel
            </button>


            <button
              type="submit"
              disabled={
                saving ||
                profilesLoading
              }
              className="rounded-lg bg-blue-600 px-5 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {
                saving
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
