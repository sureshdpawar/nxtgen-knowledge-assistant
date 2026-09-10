import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  evaluateAgentRunQuality,
  getAgentOnlineEvalResults,
  getAgentOnlineEvalSummary,
  processPendingAgentOnlineEvals,
} from "./api";


export const agentOnlineEvalQueryKeys = {
  all: [
    "agent-online-evaluation",
  ] as const,

  summary: [
    "agent-online-evaluation",
    "summary",
  ] as const,

  results: [
    "agent-online-evaluation",
    "results",
  ] as const,
};


export function useAgentOnlineEvalSummary() {
  return useQuery({
    queryKey:
      agentOnlineEvalQueryKeys.summary,

    queryFn:
      getAgentOnlineEvalSummary,
  });
}


export function useAgentOnlineEvalResults() {
  return useQuery({
    queryKey:
      agentOnlineEvalQueryKeys.results,

    queryFn:
      getAgentOnlineEvalResults,
  });
}


export function useProcessPendingAgentOnlineEvals() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn:
      processPendingAgentOnlineEvals,

    async onSuccess() {
      await queryClient
        .invalidateQueries({
          queryKey:
            agentOnlineEvalQueryKeys.all,
        });
    },
  });
}


export function useEvaluateAgentRunQuality() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: ({
      agentRunId,
    }: {
      agentRunId: string;
    }) =>
      evaluateAgentRunQuality(
        agentRunId,
      ),

    async onSuccess() {
      await queryClient
        .invalidateQueries({
          queryKey:
            agentOnlineEvalQueryKeys.all,
        });
    },
  });
}
