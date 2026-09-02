import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  getOnlineEvalResult,
  getOnlineEvalResults,
  getOnlineEvalResultsByTrace,
  getOnlineEvalSummary,
  processPendingOnlineEvals,
} from "./api";

import type {
  OnlineEvalFilters,
  OnlineEvalSummaryFilters,
} from "./types";


export const onlineEvalQueryKeys = {
  all: [
    "online-evaluation",
  ] as const,

  summary: (
    filters:
      OnlineEvalSummaryFilters,
  ) => [
    ...onlineEvalQueryKeys.all,
    "summary",
    filters,
  ] as const,

  results: (
    filters:
      OnlineEvalFilters,
  ) => [
    ...onlineEvalQueryKeys.all,
    "results",
    filters,
  ] as const,

  result: (
    resultId:
      | string
      | null,
  ) => [
    ...onlineEvalQueryKeys.all,
    "result",
    resultId,
  ] as const,

  trace: (
    sourceTraceId:
      | string
      | null,
  ) => [
    ...onlineEvalQueryKeys.all,
    "trace",
    sourceTraceId,
  ] as const,
};


export function useOnlineEvalSummary(
  filters:
    OnlineEvalSummaryFilters = {},
) {
  return useQuery({
    queryKey:
      onlineEvalQueryKeys
        .summary(
          filters,
        ),

    queryFn: () =>
      getOnlineEvalSummary(
        filters,
      ),
  });
}


export function useOnlineEvalResults(
  filters:
    OnlineEvalFilters = {},
) {
  return useQuery({
    queryKey:
      onlineEvalQueryKeys
        .results(
          filters,
        ),

    queryFn: () =>
      getOnlineEvalResults(
        filters,
      ),
  });
}


export function useOnlineEvalResult(
  resultId:
    | string
    | null,
) {
  return useQuery({
    queryKey:
      onlineEvalQueryKeys
        .result(
          resultId,
        ),

    queryFn: () =>
      getOnlineEvalResult(
        resultId!,
      ),

    enabled:
      Boolean(
        resultId,
      ),
  });
}


export function useOnlineEvalResultsByTrace(
  sourceTraceId:
    | string
    | null,
) {
  return useQuery({
    queryKey:
      onlineEvalQueryKeys
        .trace(
          sourceTraceId,
        ),

    queryFn: () =>
      getOnlineEvalResultsByTrace(
        sourceTraceId!,
      ),

    enabled:
      Boolean(
        sourceTraceId,
      ),
  });
}


export function useProcessPendingOnlineEvals() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn:
      processPendingOnlineEvals,

    async onSuccess() {
      await queryClient
        .invalidateQueries({
          queryKey:
            onlineEvalQueryKeys
              .all,
        });
    },
  });
}
