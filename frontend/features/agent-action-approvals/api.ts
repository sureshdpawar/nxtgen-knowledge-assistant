import api from "@/services/api";

import type {
  AgentActionApproval,
  AgentActionApprovalDecisionRequest,
  AgentActionApprovalStatus,
} from "./types";


export async function getAgentActionApprovals(
  status?: AgentActionApprovalStatus,
) {
  const response = await api.get<
    AgentActionApproval[]
  >(
    "/agent-action-approvals",
    {
      params: status
        ? { status }
        : undefined,
    },
  );

  return response.data;
}


export async function getAgentActionApproval(
  id: string,
) {
  const response = await api.get<
    AgentActionApproval
  >(
    `/agent-action-approvals/${id}`,
  );

  return response.data;
}


export async function approveAgentAction(
  id: string,
  payload: AgentActionApprovalDecisionRequest,
) {
  const response = await api.post<
    AgentActionApproval
  >(
    `/agent-action-approvals/${id}/approve`,
    payload,
  );

  return response.data;
}


export async function rejectAgentAction(
  id: string,
  payload: AgentActionApprovalDecisionRequest,
) {
  const response = await api.post<
    AgentActionApproval
  >(
    `/agent-action-approvals/${id}/reject`,
    payload,
  );

  return response.data;
}
