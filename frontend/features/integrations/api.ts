import api from "@/services/api";

import type {
  CreateIntegrationRequest,
  Integration,
  UpdateIntegrationRequest,
} from "./types";


export async function getIntegrations() {
  const response =
    await api.get<
      Integration[]
    >(
      "/integrations",
    );

  return response.data;
}


export async function getIntegration(
  id: string,
) {
  const response =
    await api.get<
      Integration
    >(
      `/integrations/${id}`,
    );

  return response.data;
}


export async function createIntegration(
  payload:
    CreateIntegrationRequest,
) {
  const response =
    await api.post<
      Integration
    >(
      "/integrations",
      payload,
    );

  return response.data;
}


export async function updateIntegration(
  id: string,
  payload:
    UpdateIntegrationRequest,
) {
  const response =
    await api.put<
      Integration
    >(
      `/integrations/${id}`,
      payload,
    );

  return response.data;
}


export async function deleteIntegration(
  id: string,
) {
  await api.delete(
    `/integrations/${id}`,
  );
}