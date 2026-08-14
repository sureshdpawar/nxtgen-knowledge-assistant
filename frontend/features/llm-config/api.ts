import api from "@/services/api";

import type {
  CreateLLMProfileRequest,
  LLMProfile,
  UpdateLLMProfileRequest,
} from "./types";


export async function getLLMProfiles() {
  const response =
    await api.get<LLMProfile[]>(
      "/llm-config/profiles",
    );

  return response.data;
}


export async function createLLMProfile(
  payload: CreateLLMProfileRequest,
) {
  const response =
    await api.post<LLMProfile>(
      "/llm-config/profiles",
      payload,
    );

  return response.data;
}


export async function updateLLMProfile(
  id: string,
  payload: UpdateLLMProfileRequest,
) {
  const response =
    await api.put<LLMProfile>(
      `/llm-config/profiles/${id}`,
      payload,
    );

  return response.data;
}


export async function setDefaultLLMProfile(
  id: string,
) {
  const response =
    await api.put<LLMProfile>(
      `/llm-config/profiles/${id}/default`,
    );

  return response.data;
}


export async function deleteLLMProfile(
  id: string,
) {
  await api.delete(
    `/llm-config/profiles/${id}`,
  );
}