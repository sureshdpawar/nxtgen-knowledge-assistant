import api from "@/services/api";

import type {
  AgentEvalCase,
  AgentEvalDataset,
  AgentEvalDatasetImportResponse,
  CreateAgentEvalCaseRequest,
  CreateAgentEvalDatasetRequest,
} from "./types";


export async function getAgentEvalDatasets(
  agentId?: string,
) {
  const response = await api.get<AgentEvalDataset[]>(
    "/agent-eval/datasets",
    {
      params: agentId
        ? { agent_id: agentId }
        : undefined,
    },
  );

  return response.data;
}


export async function createAgentEvalDataset(
  payload: CreateAgentEvalDatasetRequest,
) {
  const response = await api.post<AgentEvalDataset>(
    "/agent-eval/datasets",
    payload,
  );

  return response.data;
}


export async function importAgentEvalDataset(
  file: File,
) {
  const formData = new FormData();
  formData.append("file", file);

  const response =
    await api.post<AgentEvalDatasetImportResponse>(
      "/agent-eval/datasets/import",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      },
    );

  return response.data;
}


export async function getAgentEvalCases(
  datasetId: string,
) {
  const response = await api.get<AgentEvalCase[]>(
    `/agent-eval/datasets/${datasetId}/cases`,
  );

  return response.data;
}


export async function createAgentEvalCase(
  datasetId: string,
  payload: CreateAgentEvalCaseRequest,
) {
  const response = await api.post<AgentEvalCase>(
    `/agent-eval/datasets/${datasetId}/cases`,
    payload,
  );

  return response.data;
}


export async function deleteAgentEvalCase(
  datasetId: string,
  caseId: string,
) {
  await api.delete(
    `/agent-eval/datasets/${datasetId}/cases/${caseId}`,
  );
}
