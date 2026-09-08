"use client";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Bot,
  KeyRound,
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
  getAgentAccess,
  getAgents,
  replaceAgentAccess,
} from "@/features/agents/api";

import type {
  Agent,
} from "@/features/agents/types";

import type {
  User,
} from "../types";


type Props = {
  user: User;
};


type AccessByAgent = Record<
  string,
  string[]
>;


export default function ManageAgentAccess({
  user,
}: Props) {
  const [
    open,
    setOpen,
  ] = useState(false);

  const [
    agents,
    setAgents,
  ] = useState<Agent[]>([]);

  const [
    accessByAgent,
    setAccessByAgent,
  ] = useState<AccessByAgent>({});

  const [
    selectedIds,
    setSelectedIds,
  ] = useState<Set<string>>(
    new Set(),
  );

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    saving,
    setSaving,
  ] = useState(false);

  const [
    loadError,
    setLoadError,
  ] = useState<string | null>(
    null,
  );

  const [
    saveError,
    setSaveError,
  ] = useState<string | null>(
    null,
  );


  const originalAssignedIds =
    useMemo(
      () =>
        new Set(
          agents
            .filter(
              (agent) =>
                (
                  accessByAgent[
                    agent.id
                  ] ?? []
                ).includes(
                  user.id,
                ),
            )
            .map(
              (agent) =>
                agent.id,
            ),
        ),
      [
        accessByAgent,
        agents,
        user.id,
      ],
    );


  useEffect(() => {
    if (!open) {
      return;
    }

    let cancelled = false;

    async function load() {
      setLoading(true);
      setLoadError(null);
      setSaveError(null);
      setAgents([]);
      setAccessByAgent({});
      setSelectedIds(
        new Set(),
      );

      try {
        const loadedAgents =
          await getAgents();

        const accessResults =
          await Promise.all(
            loadedAgents.map(
              async (agent) => {
                const access =
                  await getAgentAccess(
                    agent.id,
                  );

                return [
                  agent.id,
                  access.user_ids,
                ] as const;
              },
            ),
          );

        if (cancelled) {
          return;
        }

        const nextAccess:
          AccessByAgent = {};

        for (
          const [
            agentId,
            userIds,
          ]
          of accessResults
        ) {
          nextAccess[
            agentId
          ] = userIds;
        }

        const nextSelected =
          new Set(
            loadedAgents
              .filter(
                (agent) =>
                  (
                    nextAccess[
                      agent.id
                    ] ?? []
                  ).includes(
                    user.id,
                  ),
              )
              .map(
                (agent) =>
                  agent.id,
              ),
          );

        setAgents(
          loadedAgents,
        );

        setAccessByAgent(
          nextAccess,
        );

        setSelectedIds(
          nextSelected,
        );
      } catch {
        if (!cancelled) {
          setLoadError(
            "Failed to load agent access.",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, [
    open,
    user.id,
  ]);


  function toggle(
    agentId: string,
  ) {
    setSelectedIds(
      (current) => {
        const next =
          new Set(
            current,
          );

        if (
          next.has(
            agentId,
          )
        ) {
          next.delete(
            agentId,
          );
        } else {
          next.add(
            agentId,
          );
        }

        return next;
      },
    );
  }


  const hasChanges =
    selectedIds.size !==
      originalAssignedIds.size ||
    Array.from(
      selectedIds,
    ).some(
      (agentId) =>
        !originalAssignedIds.has(
          agentId,
        ),
    );


  async function save() {
    setSaving(true);
    setSaveError(null);

    try {
      const changedAgents =
        agents.filter(
          (agent) =>
            selectedIds.has(
              agent.id,
            ) !==
            originalAssignedIds.has(
              agent.id,
            ),
        );

      const nextAccess = {
        ...accessByAgent,
      };

      for (
        const agent
        of changedAgents
      ) {
        const currentUserIds =
          nextAccess[
            agent.id
          ] ?? [];

        const shouldHaveAccess =
          selectedIds.has(
            agent.id,
          );

        const nextUserIds =
          shouldHaveAccess
            ? Array.from(
                new Set([
                  ...currentUserIds,
                  user.id,
                ]),
              )
            : currentUserIds.filter(
                (userId) =>
                  userId !==
                  user.id,
              );

        const updated =
          await replaceAgentAccess(
            agent.id,
            nextUserIds,
          );

        nextAccess[
          agent.id
        ] = updated.user_ids;
      }

      setAccessByAgent(
        nextAccess,
      );

      setOpen(false);
    } catch {
      setSaveError(
        "Failed to save agent access. Please try again.",
      );
    } finally {
      setSaving(false);
    }
  }


  return (
    <>
      <button
        type="button"
        onClick={() =>
          setOpen(true)
        }
        className="flex items-center gap-2 rounded-md border px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-100"
      >
        <KeyRound className="h-3.5 w-3.5" />

        Manage Agent Access
      </button>


      <Dialog
        open={open}
        onOpenChange={
          setOpen
        }
      >
        <DialogContent
          className="
            w-[calc(100vw-2rem)]
            max-w-[calc(100vw-2rem)]
            overflow-hidden
            sm:max-w-2xl
          "
        >

          <DialogHeader className="min-w-0">

            <DialogTitle>
              Manage Agent Access
            </DialogTitle>

            <DialogDescription className="break-words">
              Select the agents that{" "}
              <span className="font-medium text-slate-700">
                {user.first_name}{" "}
                {user.last_name}
              </span>{" "}
              can use in Agent Chat.
            </DialogDescription>

          </DialogHeader>


          <div className="min-w-0 py-2">

            {loading && (
              <p className="text-sm text-slate-500">
                Loading agents...
              </p>
            )}


            {loadError && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                {loadError}
              </div>
            )}


            {!loading &&
              !loadError &&
              agents.length === 0 && (
                <div className="rounded-lg border border-dashed p-6 text-center">

                  <Bot className="mx-auto h-6 w-6 text-slate-300" />

                  <p className="mt-2 text-sm text-slate-500">
                    No agents available.
                  </p>

                </div>
              )}


            {!loading &&
              !loadError &&
              agents.length > 0 && (
                <div className="max-h-96 min-w-0 space-y-2 overflow-y-auto overflow-x-hidden pr-1">

                  {agents.map(
                    (agent) => {
                      const checked =
                        selectedIds.has(
                          agent.id,
                        );

                      return (
                        <label
                          key={
                            agent.id
                          }
                          className="
                            flex
                            w-full
                            min-w-0
                            cursor-pointer
                            items-center
                            gap-3
                            overflow-hidden
                            rounded-lg
                            border
                            bg-white
                            p-3
                            hover:bg-slate-50
                          "
                        >

                          <Bot className="h-4 w-4 shrink-0 text-slate-400" />


                          <div className="min-w-0 flex-1">

                            <div className="flex min-w-0 items-center gap-2">

                              <p className="min-w-0 truncate text-sm font-medium text-slate-900">
                                {
                                  agent.name
                                }
                              </p>

                              <span className="shrink-0 rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-600">
                                {
                                  agent.status
                                }
                              </span>

                            </div>


                            {agent.description && (
                              <p
                                className="
                                  mt-1
                                  overflow-hidden
                                  text-ellipsis
                                  whitespace-nowrap
                                  text-xs
                                  text-slate-500
                                "
                                title={
                                  agent.description
                                }
                              >
                                {
                                  agent.description
                                }
                              </p>
                            )}

                          </div>


                          <input
                            type="checkbox"
                            checked={
                              checked
                            }
                            disabled={
                              saving
                            }
                            onChange={() =>
                              toggle(
                                agent.id,
                              )
                            }
                            className="h-4 w-4 shrink-0"
                          />

                        </label>
                      );
                    },
                  )}

                </div>
              )}


            {saveError && (
              <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                {saveError}
              </div>
            )}

          </div>


          <DialogFooter className="min-w-0">

            <Button
              type="button"
              variant="outline"
              disabled={
                saving
              }
              onClick={() =>
                setOpen(false)
              }
            >
              Cancel
            </Button>


            <Button
              type="button"
              disabled={
                saving ||
                loading ||
                Boolean(
                  loadError,
                ) ||
                !hasChanges
              }
              onClick={
                save
              }
            >
              {saving
                ? "Saving..."
                : "Save Access"}
            </Button>

          </DialogFooter>

        </DialogContent>
      </Dialog>
    </>
  );
}
