import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  approveAgentAction,
  getAgentActionApproval,
  getAgentActionApprovals,
  rejectAgentAction,
} from "./api";

import type {
  AgentActionApprovalDecisionRequest,
  AgentActionApprovalStatus,
} from "./types";


export function useAgentActionApprovals(
  status?: AgentActionApprovalStatus,
) {
  return useQuery({
    queryKey: [
      "agent-action-approvals",
      status ?? "ALL",
    ],
    queryFn: () =>
      getAgentActionApprovals(
        status,
      ),
  });
}


export function useAgentActionApproval(
  id: string | null,
) {
  return useQuery({
    queryKey: [
      "agent-action-approval",
      id,
    ],
    queryFn: () =>
      getAgentActionApproval(
        id!,
      ),
    enabled: Boolean(id),
  });
}


export function useApproveAgentAction() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      payload,
    }: {
      id: string;
      payload:
        AgentActionApprovalDecisionRequest;
    }) =>
      approveAgentAction(
        id,
        payload,
      ),

    onSuccess(approval) {
      queryClient.invalidateQueries({
        queryKey: [
          "agent-action-approvals",
        ],
      });

      queryClient.setQueryData(
        [
          "agent-action-approval",
          approval.id,
        ],
        approval,
      );

      queryClient.invalidateQueries({
        queryKey: [
          "agent-run",
          approval.agent_run_id,
        ],
      });

      queryClient.invalidateQueries({
        queryKey: [
          "agent-runs",
          approval.agent_id,
        ],
      });
    },
  });
}


export function useRejectAgentAction() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      payload,
    }: {
      id: string;
      payload:
        AgentActionApprovalDecisionRequest;
    }) =>
      rejectAgentAction(
        id,
        payload,
      ),

    onSuccess(approval) {
      queryClient.invalidateQueries({
        queryKey: [
          "agent-action-approvals",
        ],
      });

      queryClient.setQueryData(
        [
          "agent-action-approval",
          approval.id,
        ],
        approval,
      );

      queryClient.invalidateQueries({
        queryKey: [
          "agent-run",
          approval.agent_run_id,
        ],
      });

      queryClient.invalidateQueries({
        queryKey: [
          "agent-runs",
          approval.agent_id,
        ],
      });
    },
  });
}
