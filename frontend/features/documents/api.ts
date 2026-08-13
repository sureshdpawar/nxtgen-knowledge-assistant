import api from "@/services/api";

import type {
  Document,
} from "./types";

export async function getDocuments(
  knowledgeSourceId: string,
) {
  const response =
    await api.get<Document[]>(
      `/documents/knowledge-source/${knowledgeSourceId}`,
    );

  return response.data;
}

export async function getDocument(
  documentId: string,
) {
  const response =
    await api.get<Document>(
      `/documents/${documentId}`,
    );

  return response.data;
}

export async function uploadDocument(
  knowledgeSourceId: string,
  file: File,
) {
  const formData =
    new FormData();

  formData.append(
    "file",
    file,
  );

  const response =
    await api.post<Document>(
      `/documents/knowledge-source/${knowledgeSourceId}`,
      formData,
    );

  return response.data;
}

export async function processDocument(
  documentId: string,
) {
  const response =
    await api.post(
      `/documents/${documentId}/process`,
    );

  return response.data;
}

export async function deleteDocument(
  documentId: string,
) {
  await api.delete(
    `/documents/${documentId}`,
  );
}

export async function openDocumentFile(
  documentId: string,
  page?: number,
) {
  const response = await api.get(
    `/documents/${documentId}/file`,
    {
      responseType: "blob",
    },
  );

  const blobUrl =
    URL.createObjectURL(
      response.data,
    );

  const targetUrl =
    page
      ? `${blobUrl}#page=${page}`
      : blobUrl;

  window.open(
    targetUrl,
    "_blank",
    "noopener,noreferrer",
  );

  setTimeout(() => {
    URL.revokeObjectURL(
      blobUrl,
    );
  }, 60_000);
}