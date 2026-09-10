export interface AgentEvalToolExpectation {
  name: string;
  input_parameters: Record<string, unknown>;
}

export interface AgentEvalDataset {
  id: string;
  tenant_id: string;
  agent_id: string;
  name: string;
  version: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface AgentEvalCase {
  id: string;
  dataset_id: string;
  name: string;
  input: string;
  expected_outcome: string;
  expected_tools: AgentEvalToolExpectation[];
  forbidden_tools: string[];
  enabled: boolean;
  source_agent_run_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateAgentEvalDatasetRequest {
  agent_id: string;
  name: string;
  version?: string;
  description?: string | null;
}

export interface CreateAgentEvalCaseRequest {
  name: string;
  input: string;
  expected_outcome: string;
  expected_tools?: AgentEvalToolExpectation[];
  forbidden_tools?: string[];
  enabled?: boolean;
}

export interface AgentEvalDatasetImportResponse {
  dataset: AgentEvalDataset;
  case_count: number;
}

export type AgentEvalExperimentStatus =
  | "pending"
  | "running"
  | "passed"
  | "failed"
  | string;

export interface AgentEvalExperiment {
  id: string;
  tenant_id: string;
  dataset_id: string;
  agent_id: string;
  name: string;
  status: AgentEvalExperimentStatus;
  judge_model: string | null;
  pass_rate_threshold: number;
  case_count: number;
  passed_count: number;
  pass_rate: number | null;
  outcome_correctness: number | null;
  tool_correctness: number | null;
  argument_correctness: number | null;
  metrics: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface CreateAgentEvalExperimentRequest {
  dataset_id: string;
  name: string;
  judge_model?: string;
  pass_rate_threshold?: number;
  outcome_threshold?: number;
  tool_threshold?: number;
  argument_threshold?: number;
}

export interface AgentEvalToolCall {
  name?: string;
  input?: Record<string, unknown>;
  output?: unknown;
  status?: string;
  [key: string]: unknown;
}

export interface AgentEvalResult {
  id: string;
  experiment_id: string;
  eval_case_id: string;
  agent_run_id: string | null;
  actual_answer: string | null;
  tools_called: AgentEvalToolCall[];
  outcome_correctness: number | null;
  tool_correctness: number | null;
  argument_correctness: number | null;
  forbidden_tool_violations: string[];
  passed: boolean | null;
  metrics: Record<string, unknown>;
  judge_metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}
