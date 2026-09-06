export const AGENT_STATUSES = [
  "DRAFT",
  "ACTIVE",
  "INACTIVE",
] as const;

export type AgentStatus =
  (typeof AGENT_STATUSES)[number];

export const AGENT_RUN_STATUSES = [
  "RUNNING",
  "WAITING_FOR_APPROVAL",
  "COMPLETED",
  "FAILED",
] as const;

export type AgentRunStatus =
  (typeof AGENT_RUN_STATUSES)[number];

export const AGENT_TOOL_EXECUTION_POLICIES = [
  "AUTO",
  "HUMAN_APPROVAL",
] as const;

export type AgentToolExecutionPolicy =
  (typeof AGENT_TOOL_EXECUTION_POLICIES)[number];

export type AgentRunStepType = "LLM" | "TOOL";
export type AgentRunStepStatus = "COMPLETED" | "FAILED";
export type AgentRunApprovalStatus = "PENDING" | "APPROVED" | "REJECTED";

export interface Agent {
  id: string;
  tenant_id: string;
  created_by: string;
  name: string;
  description: string | null;
  system_prompt: string;
  llm_configuration_id: string | null;
  max_iterations: number;
  status: AgentStatus;
  knowledge_base_ids: string[];
  tool_ids: string[];
  created_at: string;
  updated_at: string;
}

export interface CreateAgentRequest {
  name: string;
  description?: string;
  system_prompt: string;
  llm_configuration_id?: string | null;
  max_iterations: number;
  status: AgentStatus;
  knowledge_base_ids: string[];
}

export interface UpdateAgentRequest {
  name?: string;
  description?: string | null;
  system_prompt?: string;
  llm_configuration_id?: string | null;
  max_iterations?: number;
  status?: AgentStatus;
  knowledge_base_ids?: string[];
}

export interface AssignAgentToolsRequest {
  tool_ids: string[];
}

export interface AgentAssignedTool {
  agent_id: string;
  tool_id: string;
  name: string;
  description: string;
  tool_type: string;
  risk_level: string;
  execution_policy: AgentToolExecutionPolicy;
  is_active: boolean;
}

export interface AgentToolPolicy {
  agent_id: string;
  tool_id: string;
  execution_policy: AgentToolExecutionPolicy;
}

export interface AgentRunRequest {
  query: string;
  thread_id?: string | null;
}

export interface AgentResumeRequest {
  decision: "approve" | "reject";
  reason?: string | null;
}

export interface AgentInterrupt {
  type?: string;
  tools?: Array<{
    name?: string;
    args?: Record<string, unknown>;
    risk_level?: string;
    execution_policy?: string;
  }>;
  [key: string]: unknown;
}

export interface AgentRunResponse {
  run_id: string;
  thread_id: string;
  checkpoint_id: string | null;
  answer: string | null;
  status: AgentRunStatus;
  llm_calls: number;
  tools_used: string[];
  duration_ms: number;
  interrupts: AgentInterrupt[];
}

export interface AgentRunStep {
  id: string;
  step_number: number;
  step_type: AgentRunStepType;
  status: AgentRunStepStatus;
  name: string;
  input_data: Record<string, unknown> | unknown[] | null;
  output_data: Record<string, unknown> | unknown[] | null;
  duration_ms: number | null;
  created_at: string;
}

export interface AgentRunApprovalAction {
  name?: string;
  args?: Record<string, unknown>;
  risk_level?: string;
  execution_policy?: string;
  [key: string]: unknown;
}

export interface AgentRunApproval {
  id: string;
  checkpoint_id: string;
  actions: AgentRunApprovalAction[];
  status: AgentRunApprovalStatus;
  requested_at: string;
  decided_at: string | null;
  decided_by_user_id: string | null;
  decision_reason: string | null;
}

export interface AgentRun {
  id: string;
  tenant_id: string;
  agent_id: string;
  user_id: string | null;
  actor_type: string;
  actor_id: string;
  context_metadata: Record<string, unknown> | null;
  thread_id: string | null;
  checkpoint_id: string | null;
  query: string;
  answer: string | null;
  status: AgentRunStatus;
  llm_calls: number;
  tools_used: string[];
  duration_ms: number | null;
  started_at: string;
  completed_at: string | null;
  created_at: string;
}

export interface AgentRunUsage {
  request_count: number;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  estimated_cost: number | null;
  currency: string | null;
  pricing_complete: boolean;
}

export interface AgentRunDetail extends AgentRun {
  error_message: string | null;
  usage: AgentRunUsage;
  steps: AgentRunStep[];
  approvals: AgentRunApproval[];
}

export interface AgentGraphMessage {
  type: string;
  id: string | null;
  content: unknown;
  name: string | null;
  tool_calls: unknown;
  tool_call_id: string | null;
}

export interface AgentGraphState {
  checkpoint_id: string | null;
  next: string[];
  created_at: string | null;
  metadata: Record<string, unknown>;
  interrupts: AgentInterrupt[];
  messages?: AgentGraphMessage[];
}

export interface AgentCheckpoint {
  checkpoint_id: string | null;
  next: string[];
  created_at: string | null;
  metadata: Record<string, unknown>;
  interrupts: AgentInterrupt[];
}

export interface AgentCheckpointHistory {
  thread_id: string;
  checkpoints: AgentCheckpoint[];
}

export type AgentProgressEvent =
  | { type: "agent_started"; run_id?: string }
  | { type: "llm_start"; step?: number }
  | { type: "llm_end"; step?: number }
  | { type: "tool_start"; tool?: string }
  | { type: "tool_end"; tool?: string }
  | { type: "approval_required"; result?: AgentRunResponse }
  | { type: "completed"; result?: AgentRunResponse }
  | { type: "error"; message?: string }
  | { type: string; [key: string]: unknown };
