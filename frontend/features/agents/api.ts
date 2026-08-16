import api from "@/services/api";

import type {
  Agent,
  AgentRun,
  AgentRunDetail,
  AgentRunRequest,
  AgentRunResponse,
  CreateAgentRequest,
  UpdateAgentRequest,
} from "./types";


export async function getAgents() {
  const response =
    await api.get<Agent[]>(
      "/agents",
    );

  return response.data;
}


export async function getAgent(
  id: string,
) {
  const response =
    await api.get<Agent>(
      `/agents/${id}`,
    );

  return response.data;
}


export async function createAgent(
  payload: CreateAgentRequest,
) {
  const response =
    await api.post<Agent>(
      "/agents",
      payload,
    );

  return response.data;
}


export async function updateAgent(
  id: string,
  payload: UpdateAgentRequest,
) {
  const response =
    await api.put<Agent>(
      `/agents/${id}`,
      payload,
    );

  return response.data;
}


export async function deleteAgent(
  id: string,
) {
  await api.delete(
    `/agents/${id}`,
  );
}


export async function runAgent(
  id: string,
  payload: AgentRunRequest,
) {
  const response =
    await api.post<
      AgentRunResponse
    >(
      `/agents/${id}/run`,
      payload,
    );

  return response.data;
}


export async function getAgentRuns(
  agentId: string,
) {
  const response =
    await api.get<
      AgentRun[]
    >(
      `/agent-runs/agent/${agentId}`,
    );

  return response.data;
}


export async function getAgentRun(
  runId: string,
) {
  const response =
    await api.get<
      AgentRunDetail
    >(
      `/agent-runs/${runId}`,
    );

  return response.data;
}