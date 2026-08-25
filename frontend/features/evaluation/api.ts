import api from "@/services/api";

import type {
  CompareEvaluationRequest,
  EvalCase,
  EvalComparison,
  EvalDataset,
  EvalDatasetImportResponse,
  EvalExperiment,
  EvalResult,
  RunRAGEvaluationRequest,
} from "./types";


export async function getEvaluationDatasets(
  knowledgeBaseId: string,
) {
  const response =
    await api.get<
      EvalDataset[]
    >(
      `/eval/knowledge-bases/${knowledgeBaseId}/datasets`,
    );

  return response.data;
}


export async function importEvaluationDataset(
  file: File,
) {
  const formData =
    new FormData();

  formData.append(
    "file",
    file,
  );

  const response =
    await api.post<
      EvalDatasetImportResponse
    >(
      "/eval/datasets/import",
      formData,
      {
        headers: {
          "Content-Type":
            "multipart/form-data",
        },
      },
    );

  return response.data;
}


export async function getEvaluationCases(
  datasetId: string,
) {
  const response =
    await api.get<
      EvalCase[]
    >(
      `/eval/datasets/${datasetId}/cases`,
    );

  return response.data;
}


export async function getEvaluationRuns(
  datasetId: string,
) {
  const response =
    await api.get<
      EvalExperiment[]
    >(
      `/eval/datasets/${datasetId}/experiments`,
    );

  return response.data;
}


export async function getEvaluationRun(
  experimentId: string,
) {
  const response =
    await api.get<
      EvalExperiment
    >(
      `/eval/experiments/${experimentId}`,
    );

  return response.data;
}


export async function getEvaluationResults(
  experimentId: string,
) {
  const response =
    await api.get<
      EvalResult[]
    >(
      `/eval/experiments/${experimentId}/results`,
    );

  return response.data;
}


export async function runRAGEvaluation(
  payload:
    RunRAGEvaluationRequest,
) {
  const response =
    await api.post<
      EvalExperiment
    >(
      "/eval/experiments/rag",
      payload,
    );

  return response.data;
}


export async function compareEvaluationRuns(
  payload:
    CompareEvaluationRequest,
) {
  const response =
    await api.post<
      EvalComparison
    >(
      "/eval/experiments/compare",
      payload,
    );

  return response.data;
}