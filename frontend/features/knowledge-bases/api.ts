import api from "@/services/api";

import type {
  CreateKnowledgeBaseRequest,
  KnowledgeBase,
  UpdateKnowledgeBaseRequest,
} from "./types";


export async function getKnowledgeBases() {
  const response =
    await api.get<KnowledgeBase[]>(
      "/knowledge-bases",
    );

  return response.data;
}


export async function createKnowledgeBase(
  payload: CreateKnowledgeBaseRequest,
) {
  const response =
    await api.post<KnowledgeBase>(
      "/knowledge-bases",
      payload,
    );

  return response.data;
}


export async function updateKnowledgeBase(
  id: string,
  payload: UpdateKnowledgeBaseRequest,
) {
  const response =
    await api.put<KnowledgeBase>(
      `/knowledge-bases/${id}`,
      payload,
    );

  return response.data;
}


export async function deleteKnowledgeBase(
  id: string,
) {
  await api.delete(
    `/knowledge-bases/${id}`,
  );
}