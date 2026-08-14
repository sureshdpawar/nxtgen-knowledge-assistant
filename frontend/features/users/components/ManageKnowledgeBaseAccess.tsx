"use client";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Database,
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
  useKnowledgeBases,
} from "@/features/knowledge-bases/hooks";

import {
  useAssignKnowledgeBase,
  useRevokeKnowledgeBase,
  useUserKnowledgeBases,
} from "../hooks";

import type {
  User,
} from "../types";


type Props = {
  user: User;
};


export default function ManageKnowledgeBaseAccess({
  user,
}: Props) {
  const [
    open,
    setOpen,
  ] =
    useState(false);


  const [
    selectedIds,
    setSelectedIds,
  ] =
    useState<Set<string>>(
      new Set(),
    );


  const {
    data:
      knowledgeBases,

    isLoading:
      knowledgeBasesLoading,

    error:
      knowledgeBasesError,
  } =
    useKnowledgeBases();


  const {
    data:
      assignedKnowledgeBases,

    isLoading:
      assignedLoading,

    error:
      assignedError,
  } =
    useUserKnowledgeBases(
      user.id,
    );


  const assignMutation =
    useAssignKnowledgeBase();


  const revokeMutation =
    useRevokeKnowledgeBase();


  const originalAssignedIds =
    useMemo(
      () =>
        new Set(
          assignedKnowledgeBases?.map(
            (
              knowledgeBase,
            ) =>
              knowledgeBase.id,
          ) ?? [],
        ),
      [
        assignedKnowledgeBases,
      ],
    );


  useEffect(() => {
    if (!open) {
      return;
    }

    setSelectedIds(
      new Set(
        originalAssignedIds,
      ),
    );
  }, [
    open,
    originalAssignedIds,
  ]);


  function toggle(
    knowledgeBaseId: string,
  ) {
    setSelectedIds(
      (
        current,
      ) => {
        const next =
          new Set(
            current,
          );

        if (
          next.has(
            knowledgeBaseId,
          )
        ) {
          next.delete(
            knowledgeBaseId,
          );
        } else {
          next.add(
            knowledgeBaseId,
          );
        }

        return next;
      },
    );
  }


  async function save() {
    const toAssign =
      Array.from(
        selectedIds,
      ).filter(
        (
          knowledgeBaseId,
        ) =>
          !originalAssignedIds.has(
            knowledgeBaseId,
          ),
      );


    const toRevoke =
      Array.from(
        originalAssignedIds,
      ).filter(
        (
          knowledgeBaseId,
        ) =>
          !selectedIds.has(
            knowledgeBaseId,
          ),
      );


    try {
      for (
        const knowledgeBaseId
        of toAssign
      ) {
        await assignMutation
          .mutateAsync({
            userId:
              user.id,

            knowledgeBaseId,
          });
      }


      for (
        const knowledgeBaseId
        of toRevoke
      ) {
        await revokeMutation
          .mutateAsync({
            userId:
              user.id,

            knowledgeBaseId,
          });
      }


      setOpen(false);

    } catch {
      // Mutation error state
      // is displayed below.
    }
  }


  const loading =
    knowledgeBasesLoading ||
    assignedLoading;


  const saving =
    assignMutation.isPending ||
    revokeMutation.isPending;


  const hasChanges =
    selectedIds.size !==
      originalAssignedIds.size ||
    Array.from(
      selectedIds,
    ).some(
      (
        knowledgeBaseId,
      ) =>
        !originalAssignedIds.has(
          knowledgeBaseId,
        ),
    );


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

        Manage KB Access
      </button>


      <Dialog
        open={open}
        onOpenChange={
          setOpen
        }
      >
        <DialogContent className="sm:max-w-xl">

          <DialogHeader>

            <DialogTitle>
              Manage Knowledge Base Access
            </DialogTitle>

            <DialogDescription>
              Select the knowledge
              bases that{" "}
              <span className="font-medium text-slate-700">
                {user.first_name}{" "}
                {user.last_name}
              </span>{" "}
              can access.
            </DialogDescription>

          </DialogHeader>


          <div className="py-2">

            {loading && (
              <p className="text-sm text-slate-500">
                Loading knowledge
                bases...
              </p>
            )}


            {(
              knowledgeBasesError ||
              assignedError
            ) && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                Failed to load
                knowledge base access.
              </div>
            )}


            {!loading &&
              !knowledgeBasesError &&
              !assignedError &&
              knowledgeBases
                ?.length === 0 && (
                <div className="rounded-lg border border-dashed p-6 text-center">

                  <Database className="mx-auto h-6 w-6 text-slate-300" />

                  <p className="mt-2 text-sm text-slate-500">
                    No knowledge
                    bases available.
                  </p>

                </div>
              )}


            {!loading &&
              !knowledgeBasesError &&
              !assignedError &&
              knowledgeBases &&
              knowledgeBases.length >
                0 && (
                <div className="max-h-96 space-y-2 overflow-y-auto pr-1">

                  {knowledgeBases.map(
                    (
                      knowledgeBase,
                    ) => {
                      const checked =
                        selectedIds.has(
                          knowledgeBase.id,
                        );

                      return (
                        <label
                          key={
                            knowledgeBase.id
                          }
                          className="flex cursor-pointer items-center justify-between gap-4 rounded-lg border bg-white p-3 hover:bg-slate-50"
                        >

                          <div className="flex min-w-0 items-center gap-3">

                            <Database className="h-4 w-4 shrink-0 text-slate-400" />


                            <div className="min-w-0">

                              <p className="truncate text-sm font-medium text-slate-900">
                                {
                                  knowledgeBase.name
                                }
                              </p>


                              {knowledgeBase.description && (
                                <p className="mt-1 truncate text-xs text-slate-500">
                                  {
                                    knowledgeBase.description
                                  }
                                </p>
                              )}

                            </div>

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
                                knowledgeBase.id,
                              )
                            }
                            className="h-4 w-4"
                          />

                        </label>
                      );
                    },
                  )}

                </div>
              )}


            {(
              assignMutation.isError ||
              revokeMutation.isError
            ) && (
              <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                Failed to save
                knowledge base
                access.
              </div>
            )}

          </div>


          <DialogFooter>

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