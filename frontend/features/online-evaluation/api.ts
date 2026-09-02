import api from "@/services/api";

import type {
  OnlineEvalFilters,
  OnlineEvalResult,
  OnlineEvalResultSummary,
  OnlineEvalSummary,
  OnlineEvalSummaryFilters,
  ProcessPendingOnlineEvalRequest,
  ProcessPendingOnlineEvalResponse,
} from "./types";


function buildParams(
  values: Record<
    string,
    unknown
  >,
) {
  return Object.fromEntries(
    Object.entries(
      values,
    ).filter(
      ([, value]) =>
        value !== undefined
        && value !== null
        && value !== "",
    ),
  );
}


export async function getOnlineEvalSummary(
  filters:
    OnlineEvalSummaryFilters = {},
) {
  const response =
    await api.get<
      OnlineEvalSummary
    >(
      "/online-eval/summary",
      {
        params:
          buildParams(
            filters,
          ),
      },
    );

  return response.data;
}


export async function getOnlineEvalResults(
  filters:
    OnlineEvalFilters = {},
) {
  const response =
    await api.get<
      OnlineEvalResultSummary[]
    >(
      "/online-eval/results",
      {
        params:
          buildParams(
            filters,
          ),
      },
    );

  return response.data;
}


export async function getOnlineEvalResult(
  resultId: string,
) {
  const response =
    await api.get<
      OnlineEvalResult
    >(
      `/online-eval/results/${resultId}`,
    );

  return response.data;
}


export async function getOnlineEvalResultsByTrace(
  sourceTraceId: string,
) {
  const response =
    await api.get<
      OnlineEvalResultSummary[]
    >(
      `/online-eval/traces/${encodeURIComponent(
        sourceTraceId,
      )}`,
    );

  return response.data;
}


export async function processPendingOnlineEvals(
  payload:
    ProcessPendingOnlineEvalRequest,
) {
  const response =
    await api.post<
      ProcessPendingOnlineEvalResponse
    >(
      "/online-eval/process-pending",
      payload,
    );

  return response.data;
}
