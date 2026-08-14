"use client";

import {
  useEffect,
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
} from "../schemas";

import type {
  KnowledgeBaseForm,
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
      // Errors are displayed
      // below.
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

      <DialogContent className="sm:max-w-xl">

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
                        profile.model_name
                      }
                      {
                        profile.is_default
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
                    defaultProfile.name
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