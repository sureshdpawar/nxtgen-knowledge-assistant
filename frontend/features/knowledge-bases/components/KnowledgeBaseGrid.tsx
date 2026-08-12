"use client";

import {
  useState,
} from "react";

import {
  useCreateKnowledgeBase,
  useDeleteKnowledgeBase,
  useKnowledgeBases,
  useUpdateKnowledgeBase,
} from "../hooks";

import type {
  KnowledgeBaseForm,
} from "../schemas";

import type {
  CreateKnowledgeBaseRequest,
  KnowledgeBase,
  UpdateKnowledgeBaseRequest,
} from "../types";

import CreateKnowledgeBaseDialog from "./CreateKnowledgeBaseDialog";
import DeleteKnowledgeBaseDialog from "./DeleteKnowledgeBaseDialog";
import EditKnowledgeBaseDialog from "./EditKnowledgeBaseDialog";
import KnowledgeBaseCard from "./KnowledgeBaseCard";


export default function KnowledgeBaseGrid() {

  const {
    data,
    isLoading,
    error,
  } =
    useKnowledgeBases();

  const createMutation =
    useCreateKnowledgeBase();

  const updateMutation =
    useUpdateKnowledgeBase();

  const deleteMutation =
    useDeleteKnowledgeBase();


  const [
    selectedKnowledgeBase,
    setSelectedKnowledgeBase,
  ] =
    useState<
      KnowledgeBase | null
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
    values:
      KnowledgeBaseForm,
  ) {

    const payload:
      CreateKnowledgeBaseRequest =
      {
        name:
          values.name,

        description:
          values.description
          || undefined,

        visibility:
          values.visibility,
      };

    await createMutation
      .mutateAsync(
        payload,
      );
  }


  function openEdit(
    knowledgeBase:
      KnowledgeBase,
  ) {
    setSelectedKnowledgeBase(
      knowledgeBase,
    );

    setEditOpen(true);
  }


  async function handleUpdate(
    id: string,
    values:
      KnowledgeBaseForm,
  ) {

    const payload:
      UpdateKnowledgeBaseRequest =
      {
        name:
          values.name,

        description:
          values.description
          || undefined,

        visibility:
          values.visibility,
      };

    await updateMutation
      .mutateAsync({
        id,
        data: payload,
      });
  }


  function openDelete(
    knowledgeBase:
      KnowledgeBase,
  ) {
    setSelectedKnowledgeBase(
      knowledgeBase,
    );

    setDeleteOpen(true);
  }


  async function handleDelete(
    id: string,
  ) {
    await deleteMutation
      .mutateAsync(id);
  }


  if (isLoading) {
    return (
      <p>
        Loading knowledge
        bases...
      </p>
    );
  }


  if (error) {
    return (
      <p className="text-red-600">
        Failed to load
        knowledge bases.
      </p>
    );
  }


  return (
    <div className="space-y-6">

      <div className="flex items-center justify-between">

        <div>
          <h1 className="text-3xl font-bold">
            Knowledge Bases
          </h1>

          <p className="mt-1 text-slate-500">
            Manage your knowledge
            repositories.
          </p>
        </div>

        <CreateKnowledgeBaseDialog
          onCreate={
            handleCreate
          }
        />

      </div>


      {!data ||
      data.length === 0 ? (

        <div className="rounded-xl border border-dashed bg-white p-12 text-center">

          <h2 className="text-lg font-semibold">
            No knowledge bases
            yet
          </h2>

          <p className="mt-2 text-sm text-slate-500">
            Create your first
            knowledge base.
          </p>

        </div>

      ) : (

        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">

          {data.map(
            (knowledgeBase) => (
              <KnowledgeBaseCard
                key={
                  knowledgeBase.id
                }
                knowledgeBase={
                  knowledgeBase
                }
                onEdit={
                  openEdit
                }
                onDelete={
                  openDelete
                }
              />
            ),
          )}

        </div>
      )}


      <EditKnowledgeBaseDialog
        knowledgeBase={
          selectedKnowledgeBase
        }
        open={
          editOpen
        }
        onOpenChange={
          setEditOpen
        }
        onUpdate={
          handleUpdate
        }
      />


      <DeleteKnowledgeBaseDialog
        knowledgeBase={
          selectedKnowledgeBase
        }
        open={
          deleteOpen
        }
        onOpenChange={
          setDeleteOpen
        }
        onDelete={
          handleDelete
        }
        deleting={
          deleteMutation
            .isPending
        }
      />

    </div>
  );
}