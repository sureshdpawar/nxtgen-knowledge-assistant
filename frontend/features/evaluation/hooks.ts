import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  compareEvaluationRuns,
  getEvaluationCases,
  getEvaluationDatasets,
  getEvaluationResults,
  getEvaluationRun,
  getEvaluationRuns,
  importEvaluationDataset,
  runRAGEvaluation,
} from "./api";


export function useEvaluationDatasets(
  knowledgeBaseId:
    | string
    | null,
) {
  return useQuery({
    queryKey: [
      "evaluation",
      "datasets",
      knowledgeBaseId,
    ],

    queryFn: () =>
      getEvaluationDatasets(
        knowledgeBaseId!,
      ),

    enabled:
      Boolean(
        knowledgeBaseId,
      ),
  });
}


export function useImportEvaluationDataset() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn:
      importEvaluationDataset,

    onSuccess(
      response,
    ) {
      queryClient
        .invalidateQueries({
          queryKey: [
            "evaluation",
            "datasets",
            response
              .dataset
              .knowledge_base_id,
          ],
        });
    },
  });
}


export function useEvaluationCases(
  datasetId:
    | string
    | null,
) {
  return useQuery({
    queryKey: [
      "evaluation",
      "cases",
      datasetId,
    ],

    queryFn: () =>
      getEvaluationCases(
        datasetId!,
      ),

    enabled:
      Boolean(
        datasetId,
      ),
  });
}


export function useEvaluationRuns(
  datasetId:
    | string
    | null,
) {
  return useQuery({
    queryKey: [
      "evaluation",
      "runs",
      datasetId,
    ],

    queryFn: () =>
      getEvaluationRuns(
        datasetId!,
      ),

    enabled:
      Boolean(
        datasetId,
      ),
  });
}


export function useEvaluationRun(
  experimentId:
    | string
    | null,
) {
  return useQuery({
    queryKey: [
      "evaluation",
      "run",
      experimentId,
    ],

    queryFn: () =>
      getEvaluationRun(
        experimentId!,
      ),

    enabled:
      Boolean(
        experimentId,
      ),
  });
}


export function useEvaluationResults(
  experimentId:
    | string
    | null,
) {
  return useQuery({
    queryKey: [
      "evaluation",
      "results",
      experimentId,
    ],

    queryFn: () =>
      getEvaluationResults(
        experimentId!,
      ),

    enabled:
      Boolean(
        experimentId,
      ),
  });
}


export function useRunRAGEvaluation() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn:
      runRAGEvaluation,

    onSuccess(
      experiment,
    ) {
      queryClient
        .invalidateQueries({
          queryKey: [
            "evaluation",
            "runs",
            experiment.dataset_id,
          ],
        });

      queryClient
        .setQueryData(
          [
            "evaluation",
            "run",
            experiment.id,
          ],
          experiment,
        );
    },
  });
}


export function useCompareEvaluationRuns() {
  return useMutation({
    mutationFn:
      compareEvaluationRuns,
  });
}