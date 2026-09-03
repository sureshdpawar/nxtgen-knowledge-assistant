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


export type AgentRunStepType =
  | "LLM"
  | "TOOL";

export type AgentRunStepStatus =
  | "COMPLETED"
  | "FAILED";


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


export interface AgentRunRequest {
  query: string;

  thread_id?: string | null;
}


export interface AgentResumeRequest {
  decision:
    | "approve"
    | "reject";

  reason?: string | null;
}


export interface AgentInterrupt {
  type?: string;

  tools?: Array<{
    name?: string;
    args?: Record<
      string,
      unknown
    >;
    risk_level?: string;
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

  input_data:
    | Record<string, unknown>
    | unknown[]
    | null;

  output_data:
    | Record<string, unknown>
    | unknown[]
    | null;

  duration_ms: number | null;

  created_at: string;
}


export interface AgentRun {
  id: string;

  tenant_id: string;
  agent_id: string;

  /*
   * Internal Agent Studio runs have a user_id.
   * Public website visitors do not.
   */
  user_id: string | null;

  /*
   * Actor identity is intentionally separate
   * from the authenticated application user.
   *
   * Examples:
   * USER
   * WEBSITE_VISITOR
   */
  actor_type: string;
  actor_id: string;

  /*
   * Correlation/business metadata.
   *
   * Keep this generic at the platform layer.
   */
  context_metadata:
    | Record<string, unknown>
    | null;

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


export interface AgentRunDetail
  extends AgentRun {
  error_message: string | null;

  usage: AgentRunUsage;

  steps: AgentRunStep[];
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

  metadata:
    Record<string, unknown>;

  interrupts: AgentInterrupt[];

  state: {
    messages?: AgentGraphMessage[];

    message_count?: number;
    llm_calls?: number;

    active_run_id?:
      | string
      | null;

    approval?: unknown;

    trace_count?: number;

    [key: string]: unknown;
  };
}


export interface AgentCheckpointHistory {
  thread_id: string;

  checkpoints:
    AgentGraphState[];
}


export type AgentProgressEvent =
  | {
      type: "run_started";
      run_id: string;
      thread_id?: string;
      agent_id: string;
      agent_name: string;
      tools: string[];
    }
  | {
      type: "llm_started";
      iteration: number;
    }
  | {
      type: "llm_completed";
      iteration: number;
      duration_ms: number;
      has_tool_calls: boolean;
      tools: string[];
    }
  | {
      type: "tool_started";
      name: string;
      args: Record<
        string,
        unknown
      >;
    }
  | {
      type: "tool_completed";
      name: string;
      duration_ms: number;
      output: unknown;
    }
  | {
      type: "approval_required";
      result: AgentRunResponse;
    }
  | {
      type: "completed";
      result: AgentRunResponse;
    }
  | {
      type: "failed";
      run_id?: string;
      thread_id?: string;
      message: string;
    };


export interface AgentProgressItem {
  id: string;

  type:
    | "LLM"
    | "TOOL";

  name: string;

  status:
    | "RUNNING"
    | "COMPLETED";

  duration_ms?: number;
}


export interface ConversationMessage {
  id: string;

  role:
    | "user"
    | "assistant"
    | "system";

  content: string;
}
