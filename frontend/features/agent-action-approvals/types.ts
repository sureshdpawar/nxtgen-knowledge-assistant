export type AgentActionApprovalStatus =
  | "PENDING"
  | "APPROVED"
  | "REJECTED";


export type AgentActionApprovalAction = {
  name?: string | null;
  args?: Record<string, unknown>;
  tool_call_id?: string | null;
  risk_level?: string | null;
  execution_policy?: string | null;
};


export type AgentActionApproval = {
  id: string;
  tenant_id: string;
  agent_id: string;
  agent_run_id: string;
  checkpoint_id: string;

  actions: AgentActionApprovalAction[];

  status: AgentActionApprovalStatus;

  requested_at: string;
  decided_at: string | null;
  decided_by_user_id: string | null;
  decision_reason: string | null;

  created_at: string;
  updated_at: string;

  agent_name: string;
  actor_type: string;
  actor_id: string;
  run_query: string;
  run_status: string;
};


export type AgentActionApprovalDecisionRequest = {
  reason?: string | null;
};
