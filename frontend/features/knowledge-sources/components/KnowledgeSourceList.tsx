"use client";

import { useState } from "react";

import {
  useCreateKnowledgeSource,
  useDeleteKnowledgeSource,
  useKnowledgeSources,
  useUpdateKnowledgeSource,
} from "../hooks";

import type {
  CreateKnowledgeSourceRequest,
  KnowledgeSource,
  UpdateKnowledgeSourceRequest,
} from "../types";

import CreateKnowledgeSourceDialog from "./CreateKnowledgeSourceDialog";
import DeleteKnowledgeSourceDialog from "./DeleteKnowledgeSourceDialog";
import EditKnowledgeSourceDialog from "./EditKnowledgeSourceDialog";
import KnowledgeSourceCard from "./KnowledgeSourceCard";

type Props = {
  knowledgeBaseId: string;
};

export default function KnowledgeSourceList({
  knowledgeBaseId,
}: Props) {
  const {
    data,
    isLoading,
    error,
  } =
    useKnowledgeSources(
      knowledgeBaseId,
    );

  const createMutation =
    useCreateKnowledgeSource(
      knowledgeBaseId,
    );

  const updateMutation =
    useUpdateKnowledgeSource(
      knowledgeBaseId,
    );

  const deleteMutation =
    useDeleteKnowledgeSource(
      knowledgeBaseId,
    );

  const [
    selectedKnowledgeSource,
    setSelectedKnowledgeSource,
  ] =
    useState<
      KnowledgeSource | null
    >(null);

  const [
    editOpen,
    setEditOpen,
  ] =
    useState(false);

  const [
    deleteOpen,
    setDeleteOpen,
  ] =
    useState(false);

  async function handleCreate(
    payload:
      CreateKnowledgeSourceRequest,
  ) {
    await createMutation.mutateAsync(
      payload,
    );
  }

  function openEdit(
    knowledgeSource:
      KnowledgeSource,
  ) {
    setSelectedKnowledgeSource(
      knowledgeSource,
    );

    setEditOpen(true);
  }

  async function handleUpdate(
    id: string,
    payload:
      UpdateKnowledgeSourceRequest,
  ) {
    await updateMutation.mutateAsync({
      id,
      data: payload,
    });
  }

  function openDelete(
    knowledgeSource:
      KnowledgeSource,
  ) {
    setSelectedKnowledgeSource(
      knowledgeSource,
    );

    setDeleteOpen(true);
  }

  async function handleDelete(
    id: string,
  ) {
    await deleteMutation.mutateAsync(
      id,
    );
  }

  if (isLoading) {
    return (
      <p className="text-sm text-slate-500">
        Loading knowledge sources...
      </p>
    );
  }

  if (error) {
    return (
      <p className="text-sm text-red-600">
        Failed to load knowledge sources.
      </p>
    );
  }

  return (
    <div className="space-y-4">

      <div className="flex items-center justify-end">
        <CreateKnowledgeSourceDialog
          onCreate={handleCreate}
        />
      </div>

      {!data ||
      data.length === 0 ? (
        <div className="rounded-xl border border-dashed bg-white p-8 text-center">

          <h3 className="font-semibold">
            No knowledge sources
          </h3>

          <p className="mt-2 text-sm text-slate-500">
            Create a source to start
            adding documents.
          </p>

        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">

          {data.map(
            (
              knowledgeSource,
            ) => (
              <KnowledgeSourceCard
                key={
                  knowledgeSource.id
                }
                knowledgeSource={
                  knowledgeSource
                }
                onEdit={openEdit}
                onDelete={openDelete}
              />
            ),
          )}

        </div>
      )}

      <EditKnowledgeSourceDialog
        knowledgeSource={
          selectedKnowledgeSource
        }
        open={editOpen}
        onOpenChange={
          setEditOpen
        }
        onUpdate={
          handleUpdate
        }
      />

      <DeleteKnowledgeSourceDialog
        knowledgeSource={
          selectedKnowledgeSource
        }
        open={deleteOpen}
        onOpenChange={
          setDeleteOpen
        }
        onDelete={
          handleDelete
        }
        deleting={
          deleteMutation.isPending
        }
      />

    </div>
  );
}