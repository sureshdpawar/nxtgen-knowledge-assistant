import api from "@/services/api";

import type {
  AgentEvalCase,
  AgentEvalDataset,
  AgentEvalDatasetImportResponse,
  AgentEvalExperiment,
  AgentEvalExperimentCompareRequest,
  AgentEvalExperimentComparison,
  AgentEvalResult,
  CreateAgentEvalCaseRequest,
  CreateAgentEvalDatasetRequest,
  CreateAgentEvalExperimentRequest,
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


export async function getAgentEvalExperiments(
  datasetId?: string,
) {
  const response = await api.get<AgentEvalExperiment[]>(
    "/agent-eval/experiments",
    {
      params: datasetId
        ? { dataset_id: datasetId }
        : undefined,
    },
  );

  return response.data;
}


export async function createAgentEvalExperiment(
  payload: CreateAgentEvalExperimentRequest,
) {
  const response = await api.post<AgentEvalExperiment>(
    "/agent-eval/experiments",
    payload,
  );

  return response.data;
}


export async function runAgentEvalExperiment(
  experimentId: string,
) {
  const response = await api.post<AgentEvalExperiment>(
    `/agent-eval/experiments/${experimentId}/run`,
  );

  return response.data;
}


export async function getAgentEvalResults(
  experimentId: string,
) {
  const response = await api.get<AgentEvalResult[]>(
    `/agent-eval/experiments/${experimentId}/results`,
  );

  return response.data;
}


export async function compareAgentEvalExperiments(
  payload: AgentEvalExperimentCompareRequest,
) {
  const response =
    await api.post<AgentEvalExperimentComparison>(
      "/agent-eval/experiments/compare",
      payload,
    );

  return response.data;
}
