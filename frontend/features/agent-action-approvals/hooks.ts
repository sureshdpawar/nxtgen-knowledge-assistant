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
  AgentActionApproval,
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


function updateApprovalCaches(
  queryClient:
    ReturnType<
      typeof useQueryClient
    >,
  approval:
    AgentActionApproval,
) {
  /*
   * Update the individual approval immediately.
   */
  queryClient.setQueryData(
    [
      "agent-action-approval",
      approval.id,
    ],
    approval,
  );


  /*
   * A decided approval must disappear immediately
   * from the PENDING list.
   */
  queryClient.setQueryData<
    AgentActionApproval[]
  >(
    [
      "agent-action-approvals",
      "PENDING",
    ],
    (
      current = [],
    ) =>
      current.filter(
        (item) =>
          item.id
          !== approval.id,
      ),
  );


  /*
   * Add/update it immediately in its destination list.
   */
  queryClient.setQueryData<
    AgentActionApproval[]
  >(
    [
      "agent-action-approvals",
      approval.status,
    ],
    (
      current = [],
    ) => {
      const withoutCurrent =
        current.filter(
          (item) =>
            item.id
            !== approval.id,
        );

      return [
        approval,
        ...withoutCurrent,
      ];
    },
  );


  /*
   * If an unfiltered list is ever used,
   * keep that cache consistent too.
   */
  queryClient.setQueryData<
    AgentActionApproval[]
  >(
    [
      "agent-action-approvals",
      "ALL",
    ],
    (
      current = [],
    ) =>
      current.map(
        (item) =>
          item.id
          === approval.id
            ? approval
            : item,
      ),
  );
}


async function refreshRelatedQueries(
  queryClient:
    ReturnType<
      typeof useQueryClient
    >,
  approval:
    AgentActionApproval,
) {
  /*
   * Revalidate against the backend after the
   * immediate cache update.
   *
   * The immediate cache change gives correct UX.
   * The refetch keeps the browser synchronized
   * with the authoritative backend state.
   */
  await Promise.all([
    queryClient.invalidateQueries({
      queryKey: [
        "agent-action-approvals",
      ],
    }),

    queryClient.invalidateQueries({
      queryKey: [
        "agent-run",
        approval.agent_run_id,
      ],
    }),

    queryClient.invalidateQueries({
      queryKey: [
        "agent-runs",
        approval.agent_id,
      ],
    }),
  ]);
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

    async onSuccess(
      approval,
    ) {
      updateApprovalCaches(
        queryClient,
        approval,
      );

      await refreshRelatedQueries(
        queryClient,
        approval,
      );
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

    async onSuccess(
      approval,
    ) {
      updateApprovalCaches(
        queryClient,
        approval,
      );

      await refreshRelatedQueries(
        queryClient,
        approval,
      );
    },
  });
}