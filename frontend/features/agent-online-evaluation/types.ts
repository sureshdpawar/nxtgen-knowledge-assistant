export type AgentOnlineEvalCapability = {
  name?: string;
  description?: string;
  kind?: string;
  risk_level?: string;
  execution_policy?: string;
};

export type AgentOnlineEvalTaskQualityMetric = {
  score?: number | null;
  passed?: boolean;
  reason?: string;
  usage?: Record<string, unknown>;
  latency_ms?: number;
  evaluator?: Record<string, unknown>;
  threshold?: number;
};

export type AgentOnlineEvalCapabilityGroundingMetric = {
  runtime_capabilities?:
    AgentOnlineEvalCapability[];
  tools_executed?: string[];
  snapshot_source?: string;
};

export type AgentOnlineEvalMetrics = {
  task_quality?:
    AgentOnlineEvalTaskQualityMetric;
  capability_grounding?:
    AgentOnlineEvalCapabilityGroundingMetric;
  execution_health?:
    Record<string, unknown>;
  [key: string]: unknown;
};

export type AgentOnlineEvalResult = {
  id: string;
  tenant_id: string;
  agent_id: string;
  agent_run_id: string;

  status: string;
  sample_reason: string;

  question: string;
  actual_answer: string | null;
  tools_used: string[];

  task_quality_score: number | null;
  execution_health_score: number | null;
  overall_score: number | null;

  passed: boolean | null;
  evaluated_at: string | null;
  error_message: string | null;

  metrics: AgentOnlineEvalMetrics;
  evaluation_metadata:
    Record<string, unknown>;

  created_at: string;
  updated_at: string;
};

export type AgentOnlineEvalSummary = {
  total: number;
  pending: number;
  completed: number;
  failed: number;
  passed: number;
  failed_quality: number;
  pass_rate: number | null;
  average_task_quality: number | null;
  average_execution_health: number | null;
  average_overall_score: number | null;
};

export type AgentOnlineEvalProcessRequest = {
  limit: number;
  evaluator_llm_configuration_id?: string | null;
  task_quality_threshold: number;
};

export type AgentOnlineEvalProcessResponse = {
  requested: number;
  processed: number;
  completed: number;
  failed: number;
  result_ids: string[];
};

export type AgentOnlineEvalRunRequest = {
  evaluator_llm_configuration_id?: string | null;
  task_quality_threshold?: number;
};
