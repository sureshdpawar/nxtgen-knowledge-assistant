import api from "@/services/api";

import type {
  AgentOnlineEvalProcessRequest,
  AgentOnlineEvalProcessResponse,
  AgentOnlineEvalResult,
  AgentOnlineEvalRunRequest,
  AgentOnlineEvalSummary,
} from "./types";


export async function getAgentOnlineEvalSummary() {
  const response =
    await api.get<
      AgentOnlineEvalSummary
    >(
      "/agent-eval/online/summary",
    );

  return response.data;
}


export async function getAgentOnlineEvalResults() {
  const response =
    await api.get<
      AgentOnlineEvalResult[]
    >(
      "/agent-eval/online/results",
      {
        params: {
          limit: 100,
        },
      },
    );

  return response.data;
}


export async function processPendingAgentOnlineEvals(
  payload:
    AgentOnlineEvalProcessRequest,
) {
  const response =
    await api.post<
      AgentOnlineEvalProcessResponse
    >(
      "/agent-eval/online/process-pending",
      payload,
    );

  return response.data;
}


export async function evaluateAgentRunQuality(
  agentRunId: string,
  payload:
    AgentOnlineEvalRunRequest = {},
) {
  const response =
    await api.post<
      AgentOnlineEvalResult
    >(
      `/agent-eval/online/runs/${agentRunId}/evaluate`,
      {
        task_quality_threshold:
          payload.task_quality_threshold
          ?? 0.8,
        evaluator_llm_configuration_id:
          payload
            .evaluator_llm_configuration_id
          ?? null,
      },
    );

  return response.data;
}
