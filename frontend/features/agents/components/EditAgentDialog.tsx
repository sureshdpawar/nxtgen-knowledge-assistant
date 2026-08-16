"use client";

import {
  type FormEvent,
  useState,
} from "react";

import {
  Pencil,
} from "lucide-react";

import {
  Button,
} from "@/components/ui/button";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import {
  useKnowledgeBases,
} from "@/features/knowledge-bases/hooks";

import {
  useLLMProfiles,
} from "@/features/llm-config/hooks";

import {
  useUpdateAgent,
} from "../hooks";

import {
  AGENT_STATUSES,
} from "../types";

import type {
  Agent,
  AgentStatus,
} from "../types";


type Props = {
  agent: Agent;
};


export default function EditAgentDialog({
  agent,
}: Props) {
  const mutation =
    useUpdateAgent();

  const llmProfilesQuery =
    useLLMProfiles();

  const knowledgeBasesQuery =
    useKnowledgeBases();


  const [
    open,
    setOpen,
  ] = useState(false);

  const [
    name,
    setName,
  ] = useState(
    agent.name,
  );

  const [
    description,
    setDescription,
  ] = useState(
    agent.description ?? "",
  );

  const [
    systemPrompt,
    setSystemPrompt,
  ] = useState(
    agent.system_prompt,
  );

  const [
    llmConfigurationId,
    setLLMConfigurationId,
  ] = useState(
    agent.llm_configuration_id
      ?? "",
  );

  const [
    maxIterations,
    setMaxIterations,
  ] = useState(
    String(
      agent.max_iterations,
    ),
  );

  const [
    agentStatus,
    setAgentStatus,
  ] = useState<AgentStatus>(
    agent.status,
  );

  const [
    knowledgeBaseIds,
    setKnowledgeBaseIds,
  ] = useState<string[]>(
    agent.knowledge_base_ids,
  );


  function resetForm() {
    setName(
      agent.name,
    );

    setDescription(
      agent.description
        ?? "",
    );

    setSystemPrompt(
      agent.system_prompt,
    );

    setLLMConfigurationId(
      agent.llm_configuration_id
        ?? "",
    );

    setMaxIterations(
      String(
        agent.max_iterations,
      ),
    );

    setAgentStatus(
      agent.status,
    );

    setKnowledgeBaseIds(
      agent.knowledge_base_ids,
    );
  }


  function handleOpenChange(
    nextOpen: boolean,
  ) {
    setOpen(
      nextOpen,
    );

    if (nextOpen) {
      resetForm();
    }
  }


  function handleStatusChange(
    value: string,
  ) {
    if (
      AGENT_STATUSES.includes(
        value as AgentStatus,
      )
    ) {
      setAgentStatus(
        value as AgentStatus,
      );
    }
  }


  function toggleKnowledgeBase(
    id: string,
  ) {
    setKnowledgeBaseIds(
      (current) => {
        if (
          current.includes(id)
        ) {
          return current.filter(
            (value) =>
              value !== id,
          );
        }

        return [
          ...current,
          id,
        ];
      },
    );
  }


  async function submit(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (
      !name.trim() ||
      !systemPrompt.trim()
    ) {
      return;
    }

    const parsedMaxIterations =
      Number(maxIterations);

    if (
      !Number.isFinite(
        parsedMaxIterations,
      ) ||
      parsedMaxIterations < 1
    ) {
      return;
    }

    try {
      await mutation.mutateAsync({
        id:
          agent.id,

        data: {
          name:
            name.trim(),

          description:
            description.trim()
              || null,

          system_prompt:
            systemPrompt.trim(),

          llm_configuration_id:
            llmConfigurationId
              || null,

          max_iterations:
            parsedMaxIterations,

          status:
            agentStatus,

          knowledge_base_ids:
            knowledgeBaseIds,
        },
      });

      setOpen(false);

    } catch {
      // Mutation error rendered below.
    }
  }


  return (
    <>
      <Button
        type="button"
        variant="outline"
        onClick={() =>
          handleOpenChange(
            true,
          )
        }
      >
        <Pencil className="mr-2 h-4 w-4" />

        Edit
      </Button>


      <Dialog
        open={open}
        onOpenChange={
          handleOpenChange
        }
      >
        <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-2xl">

          <DialogHeader>

            <DialogTitle>
              Edit Agent
            </DialogTitle>

            <DialogDescription>
              Update agent behavior,
              model configuration,
              and knowledge access.
            </DialogDescription>

          </DialogHeader>


          <form
            onSubmit={submit}
            className="space-y-6"
          >

            <div>

              <label className="text-sm font-medium text-slate-700">
                Name
              </label>

              <input
                value={name}
                onChange={(event) =>
                  setName(
                    event.target.value,
                  )
                }
                className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm outline-none focus:border-blue-500"
              />

            </div>


            <div>

              <label className="text-sm font-medium text-slate-700">
                Description
              </label>

              <textarea
                value={description}
                onChange={(event) =>
                  setDescription(
                    event.target.value,
                  )
                }
                rows={3}
                className="mt-2 w-full rounded-md border border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-500"
              />

            </div>


            <div>

              <label className="text-sm font-medium text-slate-700">
                System Instructions
              </label>

              <textarea
                value={systemPrompt}
                onChange={(event) =>
                  setSystemPrompt(
                    event.target.value,
                  )
                }
                rows={6}
                className="mt-2 w-full rounded-md border border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-500"
              />

            </div>


            <div className="grid gap-4 md:grid-cols-2">

              <div>

                <label className="text-sm font-medium text-slate-700">
                  LLM Profile
                </label>

                <select
                  value={
                    llmConfigurationId
                  }
                  onChange={(event) =>
                    setLLMConfigurationId(
                      event.target.value,
                    )
                  }
                  className="mt-2 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
                >

                  <option value="">
                    Use Tenant Default
                  </option>


                  {llmProfilesQuery.data
                    ?.filter(
                      (profile) =>
                        profile.is_active,
                    )
                    .map(
                      (profile) => (
                        <option
                          key={profile.id}
                          value={profile.id}
                        >
                          {profile.name}
                          {" — "}
                          {profile.model_name}
                        </option>
                      ),
                    )}

                </select>

              </div>


              <div>

                <label className="text-sm font-medium text-slate-700">
                  Maximum Steps
                </label>

                <input
                  type="number"
                  min={1}
                  max={20}
                  value={
                    maxIterations
                  }
                  onChange={(event) =>
                    setMaxIterations(
                      event.target.value,
                    )
                  }
                  className="mt-2 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                />

              </div>

            </div>


            <div>

              <label className="text-sm font-medium text-slate-700">
                Status
              </label>

              <select
                value={agentStatus}
                onChange={(event) =>
                  handleStatusChange(
                    event.target.value,
                  )
                }
                className="mt-2 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
              >

                <option value="DRAFT">
                  Draft
                </option>

                <option value="ACTIVE">
                  Active
                </option>

                <option value="INACTIVE">
                  Inactive
                </option>

              </select>

            </div>


            <div>

              <div className="flex items-center justify-between">

                <label className="text-sm font-medium text-slate-700">
                  Knowledge Bases
                </label>

                <span className="text-xs text-slate-400">
                  {knowledgeBaseIds.length}{" "}
                  selected
                </span>

              </div>


              <div className="mt-2 max-h-52 space-y-2 overflow-y-auto rounded-lg border p-3">

                {knowledgeBasesQuery.isLoading && (
                  <p className="text-sm text-slate-500">
                    Loading knowledge
                    bases...
                  </p>
                )}


                {knowledgeBasesQuery.isError && (
                  <p className="text-sm text-red-600">
                    Failed to load
                    knowledge bases.
                  </p>
                )}


                {knowledgeBasesQuery.data?.map(
                  (
                    knowledgeBase,
                  ) => (
                    <label
                      key={
                        knowledgeBase.id
                      }
                      className="flex cursor-pointer items-start gap-3 rounded-md p-2 hover:bg-slate-50"
                    >

                      <input
                        type="checkbox"
                        checked={
                          knowledgeBaseIds.includes(
                            knowledgeBase.id,
                          )
                        }
                        onChange={() =>
                          toggleKnowledgeBase(
                            knowledgeBase.id,
                          )
                        }
                        className="mt-1"
                      />


                      <div>

                        <p className="text-sm font-medium text-slate-800">
                          {
                            knowledgeBase.name
                          }
                        </p>

                        {knowledgeBase.description && (
                          <p className="mt-1 text-xs text-slate-500">
                            {
                              knowledgeBase.description
                            }
                          </p>
                        )}

                      </div>

                    </label>
                  ),
                )}

              </div>

            </div>


            {mutation.isError && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                Failed to update
                agent.
              </div>
            )}


            <DialogFooter>

              <Button
                type="button"
                variant="outline"
                onClick={() =>
                  handleOpenChange(
                    false,
                  )
                }
                disabled={
                  mutation.isPending
                }
              >
                Cancel
              </Button>


              <Button
                type="submit"
                disabled={
                  mutation.isPending ||
                  !name.trim() ||
                  !systemPrompt.trim()
                }
              >
                {mutation.isPending
                  ? "Saving..."
                  : "Save Changes"}
              </Button>

            </DialogFooter>

          </form>

        </DialogContent>
      </Dialog>
    </>
  );
}