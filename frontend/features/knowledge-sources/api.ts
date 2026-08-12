import api from "@/services/api";

import type {
  CreateKnowledgeSourceRequest,
  KnowledgeSource,
  UpdateKnowledgeSourceRequest,
} from "./types";

export async function getKnowledgeSources(
  knowledgeBaseId: string,
) {
  const response =
    await api.get<KnowledgeSource[]>(
      `/knowledge-sources/knowledge-base/${knowledgeBaseId}`,
    );

  return response.data;
}

export async function getKnowledgeSource(
  knowledgeSourceId: string,
) {
  const response =
    await api.get<KnowledgeSource>(
      `/knowledge-sources/${knowledgeSourceId}`,
    );

  return response.data;
}

export async function createKnowledgeSource(
  knowledgeBaseId: string,
  payload: CreateKnowledgeSourceRequest,
) {
  const response =
    await api.post<KnowledgeSource>(
      `/knowledge-sources/knowledge-base/${knowledgeBaseId}`,
      payload,
    );

  return response.data;
}

export async function updateKnowledgeSource(
  knowledgeSourceId: string,
  payload: UpdateKnowledgeSourceRequest,
) {
  const response =
    await api.put<KnowledgeSource>(
      `/knowledge-sources/${knowledgeSourceId}`,
      payload,
    );

  return response.data;
}

export async function deleteKnowledgeSource(
  knowledgeSourceId: string,
) {
  await api.delete(
    `/knowledge-sources/${knowledgeSourceId}`,
  );
}