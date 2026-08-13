import api from "@/services/api";

import type {
  SearchRequest,
  SearchResponse,
} from "./types";


export async function searchKnowledgeBase(
  payload: SearchRequest,
) {
  const response =
    await api.post<SearchResponse>(
      "/search",
      payload,
    );

  return response.data;
}