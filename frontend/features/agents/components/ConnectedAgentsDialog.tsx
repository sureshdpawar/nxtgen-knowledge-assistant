"use client";

import {
  useEffect,
  useState,
} from "react";

import {
  Network,
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
  useAgentA2AConnections,
  useReplaceAgentA2AConnections,
} from "../a2a-connections";

import type {
  Agent,
} from "../types";


type Props = {
  agent: Agent;
  agents: Agent[];
};


export default function ConnectedAgentsDialog({
  agent,
  agents,
}: Props) {
  const [
    open,
    setOpen,
  ] = useState(
    false,
  );

  const [
    selectedIds,
    setSelectedIds,
  ] = useState<string[]>(
    [],
  );

  const [
    localError,
    setLocalError,
  ] = useState<
    string | null
  >(null);

  const connectionsQuery =
    useAgentA2AConnections(
      agent.id,
      open,
    );

  const replaceMutation =
    useReplaceAgentA2AConnections();

  const candidates = agents.filter(
    (candidate) =>
      candidate.id !== agent.id
      && candidate.status === "ACTIVE",
  );

  useEffect(
    () => {
      if (
        !open
        || !connectionsQuery.data
      ) {
        return;
      }

      setSelectedIds(
        connectionsQuery.data.map(
          (connection) =>
            connection.target_agent_id,
        ),
      );
    }, [
      open,
      connectionsQuery.data,
    ],
  );

  function handleOpenChange(
    nextOpen: boolean,
  ) {
    setOpen(
      nextOpen,
    );

    if (nextOpen) {
      setSelectedIds(
        [],
      );
      setLocalError(
        null,
      );
    }
  }

  function toggleAgent(
    targetAgentId: string,
  ) {
    setSelectedIds(
      (current) =>
        current.includes(
          targetAgentId,
        )
          ? current.filter(
              (value) =>
                value !== targetAgentId,
            )
          : [
              ...current,
              targetAgentId,
            ],
    );
  }

  async function save() {
    setLocalError(
      null,
    );

    try {
      await replaceMutation.mutateAsync({
        agentId:
          agent.id,
        targetAgentIds:
          selectedIds,
      });

      setOpen(
        false,
      );
    } catch {
      setLocalError(
        "Failed to save connected agents.",
      );
    }
  }

  const isSaving =
    replaceMutation.isPending;

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
        <Network className="mr-2 h-4 w-4" />
        Connected Agents
      </Button>

      <Dialog
        open={open}
        onOpenChange={
          handleOpenChange
        }
      >
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              Connected Agents
            </DialogTitle>

            <DialogDescription>
              Allow {agent.name} to discover and delegate
              specialist work to selected agents using A2A v1.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="rounded-lg border border-violet-200 bg-violet-50 p-3">
              <div className="flex flex-wrap items-center gap-2">
                <Network className="h-4 w-4 text-violet-700" />
                <span className="text-sm font-semibold text-violet-900">
                  Agent-to-Agent delegation
                </span>
                <span className="rounded-full bg-white px-2 py-0.5 text-[11px] font-semibold text-violet-700">
                  A2A v1
                </span>
              </div>

              <p className="mt-2 text-xs leading-5 text-violet-800">
                Connected agents keep their own prompt, knowledge,
                tools, governance, and AgentRun. This connection
                only grants delegation/discovery capability.
              </p>
            </div>

            {connectionsQuery.isLoading && (
              <div className="rounded-lg border p-4 text-sm text-slate-500">
                Loading connected agents...
              </div>
            )}

            {connectionsQuery.isError && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                Failed to load connected agents.
              </div>
            )}

            {!connectionsQuery.isLoading
              && !connectionsQuery.isError
              && candidates.length === 0 && (
                <div className="rounded-lg border border-dashed p-5 text-sm text-slate-500">
                  No other active agents are available. Create and
                  activate a second specialist agent first.
                </div>
              )}

            {!connectionsQuery.isLoading
              && candidates.length > 0 && (
                <div className="max-h-96 space-y-3 overflow-y-auto">
                  {candidates.map(
                    (candidate) => {
                      const selected =
                        selectedIds.includes(
                          candidate.id,
                        );

                      return (
                        <label
                          key={candidate.id}
                          className="flex cursor-pointer items-start gap-3 rounded-lg border border-slate-200 p-4 hover:bg-slate-50"
                        >
                          <input
                            type="checkbox"
                            checked={selected}
                            onChange={() =>
                              toggleAgent(
                                candidate.id,
                              )
                            }
                            className="mt-1"
                          />

                          <div className="min-w-0 flex-1">
                            <div className="flex flex-wrap items-center gap-2">
                              <p className="text-sm font-semibold text-slate-900">
                                {candidate.name}
                              </p>

                              <span className="rounded-full bg-green-50 px-2 py-0.5 text-[11px] font-medium text-green-700">
                                ACTIVE
                              </span>

                              <span className="rounded-full bg-violet-50 px-2 py-0.5 text-[11px] font-medium text-violet-700">
                                A2A v1
                              </span>
                            </div>

                            <p className="mt-1 text-xs leading-5 text-slate-500">
                              {candidate.description
                                || "No capability description provided."}
                            </p>

                            {selected && (
                              <p className="mt-2 text-xs font-medium text-violet-700">
                                Discoverable at runtime by {agent.name}
                              </p>
                            )}
                          </div>
                        </label>
                      );
                    },
                  )}
                </div>
              )}

            {localError && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                {localError}
              </div>
            )}
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() =>
                handleOpenChange(
                  false,
                )
              }
              disabled={isSaving}
            >
              Cancel
            </Button>

            <Button
              type="button"
              onClick={save}
              disabled={
                isSaving
                || connectionsQuery.isLoading
                || connectionsQuery.isError
              }
            >
              {isSaving
                ? "Saving..."
                : "Save Connections"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
