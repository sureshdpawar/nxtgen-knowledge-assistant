export const AGENT_STATUSES = [
  "DRAFT",
  "ACTIVE",
  "INACTIVE",
] as const;


export type AgentStatus =
  (typeof AGENT_STATUSES)[number];


export const AGENT_RUN_STATUSES = [
  "RUNNING",
  "COMPLETED",
  "FAILED",
] as const;


export type AgentRunStatus =
  (typeof AGENT_RUN_STATUSES)[number];


export const AGENT_RUN_STEP_TYPES = [
  "LLM",
  "TOOL",
] as const;


export type AgentRunStepType =
  (typeof AGENT_RUN_STEP_TYPES)[number];


export const AGENT_RUN_STEP_STATUSES = [
  "COMPLETED",
  "FAILED",
] as const;


export type AgentRunStepStatus =
  (typeof AGENT_RUN_STEP_STATUSES)[number];


export interface Agent {
  id: string;

  tenant_id: string;

  created_by: string;

  name: string;

  description: string | null;

  system_prompt: string;

  llm_configuration_id:
    string | null;

  max_iterations: number;

  status: AgentStatus;

  knowledge_base_ids:
    string[];

  created_at: string;

  updated_at: string;
}


export interface CreateAgentRequest {
  name: string;

  description?: string;

  system_prompt: string;

  llm_configuration_id?:
    string | null;

  max_iterations: number;

  status: AgentStatus;

  knowledge_base_ids:
    string[];
}


export interface UpdateAgentRequest {
  name?: string;

  description?: string | null;

  system_prompt?: string;

  llm_configuration_id?:
    string | null;

  max_iterations?: number;

  status?: AgentStatus;

  knowledge_base_ids?:
    string[];
}


export interface AgentRunRequest {
  query: string;
}


export interface AgentRunResponse {
  run_id: string;

  answer: string;

  status: AgentRunStatus;

  llm_calls: number;

  tools_used: string[];

  duration_ms: number;
}


export interface AgentRunStep {
  id: string;

  step_number: number;

  step_type:
    AgentRunStepType;

  status:
    AgentRunStepStatus;

  name: string;

  input_data:
    Record<string, unknown>
    | unknown[]
    | null;

  output_data:
    Record<string, unknown>
    | unknown[]
    | null;

  duration_ms:
    number | null;

  created_at: string;
}


export interface AgentRun {
  id: string;

  tenant_id: string;

  agent_id: string;

  user_id: string;

  query: string;

  answer: string | null;

  status: AgentRunStatus;

  llm_calls: number;

  tools_used: string[];

  duration_ms:
    number | null;

  started_at: string;

  completed_at:
    string | null;

  created_at: string;
}


export interface AgentRunDetail
  extends AgentRun {

  error_message:
    string | null;

  steps:
    AgentRunStep[];
}