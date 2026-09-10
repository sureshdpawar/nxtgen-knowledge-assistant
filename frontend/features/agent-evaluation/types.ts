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

export interface PromoteAgentRunRequest {
  agent_run_id: string;
  name: string;
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

export interface AgentEvalExperimentCompareRequest {
  baseline_experiment_id: string;
  candidate_experiment_id: string;
}

export interface AgentEvalMetricDelta {
  baseline: number | null;
  candidate: number | null;
  delta: number | null;
}

export type AgentEvalCaseClassification =
  | "regression"
  | "improvement"
  | "unchanged"
  | "missing_result"
  | string;

export interface AgentEvalCaseComparison {
  eval_case_id: string;
  case_name: string;
  baseline_result_id: string | null;
  candidate_result_id: string | null;
  baseline_passed: boolean | null;
  candidate_passed: boolean | null;
  classification: AgentEvalCaseClassification;
  outcome_correctness: AgentEvalMetricDelta;
  tool_correctness: AgentEvalMetricDelta;
  argument_correctness: AgentEvalMetricDelta;
  baseline_forbidden_tool_violations: string[];
  candidate_forbidden_tool_violations: string[];
}

export interface AgentEvalExperimentComparison {
  baseline_experiment: AgentEvalExperiment;
  candidate_experiment: AgentEvalExperiment;
  pass_rate: AgentEvalMetricDelta;
  outcome_correctness: AgentEvalMetricDelta;
  tool_correctness: AgentEvalMetricDelta;
  argument_correctness: AgentEvalMetricDelta;
  regressions: number;
  improvements: number;
  unchanged: number;
  missing_results: number;
  cases: AgentEvalCaseComparison[];
}
