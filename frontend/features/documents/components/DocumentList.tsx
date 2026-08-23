"use client";

import {
  useState,
} from "react";

import {
  useDeleteDocument,
  useDocuments,
  useProcessDocument,
  useUploadDocument,
} from "../hooks";

import type {
  Document,
} from "../types";

import DeleteDocumentDialog from "./DeleteDocumentDialog";
import DocumentCard from "./DocumentCard";
import UploadDocumentDialog from "./UploadDocumentDialog";


type Props = {
  knowledgeSourceId: string;

  allowUpload?: boolean;

  allowManualProcess?: boolean;

  allowDelete?: boolean;

  emptyTitle?: string;

  emptyDescription?: string;
};


export default function DocumentList({
  knowledgeSourceId,
  allowUpload = true,
  allowManualProcess = true,
  allowDelete = true,
  emptyTitle = "No documents",
  emptyDescription = (
    "Upload a document to "
    + "this knowledge source."
  ),
}: Props) {
  const {
    data,
    isLoading,
    error,
  } =
    useDocuments(
      knowledgeSourceId,
    );

  const uploadMutation =
    useUploadDocument(
      knowledgeSourceId,
    );

  const processMutation =
    useProcessDocument(
      knowledgeSourceId,
    );

  const deleteMutation =
    useDeleteDocument(
      knowledgeSourceId,
    );

  const [
    selectedDocument,
    setSelectedDocument,
  ] =
    useState<Document | null>(
      null,
    );

  const [
    deleteOpen,
    setDeleteOpen,
  ] =
    useState(false);


  async function handleUpload(
    file: File,
  ) {
    await uploadMutation
      .mutateAsync(file);
  }


  async function handleProcess(
    document: Document,
  ) {
    if (!allowManualProcess) {
      return;
    }

    await processMutation
      .mutateAsync(
        document.id,
      );
  }


  function openDelete(
    document: Document,
  ) {
    if (!allowDelete) {
      return;
    }

    setSelectedDocument(
      document,
    );

    setDeleteOpen(true);
  }


  async function handleDelete(
    documentId: string,
  ) {
    await deleteMutation
      .mutateAsync(
        documentId,
      );
  }


  if (isLoading) {
    return (
      <p className="text-sm text-slate-500">
        Loading documents...
      </p>
    );
  }


  if (error) {
    return (
      <p className="text-sm text-red-600">
        Failed to load documents.
      </p>
    );
  }


  return (
    <div className="space-y-4">

      {allowUpload && (
        <div className="flex items-center justify-end">

          <UploadDocumentDialog
            onUpload={
              handleUpload
            }
          />

        </div>
      )}


      {!data ||
      data.length === 0 ? (
        <div className="rounded-xl border border-dashed bg-white p-8 text-center">

          <h3 className="font-semibold text-slate-900">
            {emptyTitle}
          </h3>

          <p className="mt-2 text-sm text-slate-500">
            {emptyDescription}
          </p>

        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">

          {data.map(
            (
              document,
            ) => (
              <DocumentCard
                key={
                  document.id
                }
                document={
                  document
                }
                onProcess={
                  allowManualProcess
                    ? handleProcess
                    : undefined
                }
                onDelete={
                  allowDelete
                    ? openDelete
                    : undefined
                }
                processing={
                  allowManualProcess
                  && processMutation
                    .isPending
                  && processMutation
                    .variables
                    === document.id
                }
                showProcessAction={
                  allowManualProcess
                }
                showDeleteAction={
                  allowDelete
                }
              />
            ),
          )}

        </div>
      )}


      {allowDelete && (
        <DeleteDocumentDialog
          document={
            selectedDocument
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
      )}

    </div>
  );
}