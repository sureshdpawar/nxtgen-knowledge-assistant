import api from "@/services/api";

import type {
  CreateToolRequest,
  ToolDefinition,
  UpdateToolRequest,
} from "./types";


export async function getTools() {
  const response =
    await api.get<
      ToolDefinition[]
    >(
      "/tools",
    );

  return response.data;
}


export async function createTool(
  payload:
    CreateToolRequest,
) {
  const response =
    await api.post<
      ToolDefinition
    >(
      "/tools",
      payload,
    );

  return response.data;
}


export async function updateTool(
  id: string,
  payload:
    UpdateToolRequest,
) {
  const response =
    await api.put<
      ToolDefinition
    >(
      `/tools/${id}`,
      payload,
    );

  return response.data;
}


export async function deleteTool(
  id: string,
) {
  await api.delete(
    `/tools/${id}`,
  );
}