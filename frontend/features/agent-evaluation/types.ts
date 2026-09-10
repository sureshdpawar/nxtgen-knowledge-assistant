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
