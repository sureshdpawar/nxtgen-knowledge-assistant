export type OnlineEvalStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed";

export type OnlineEvalOutcome =
  | "pass"
  | "safe_abstention"
  | "fail";

export type OnlineEvalAverageScores = {
  faithfulness: number | null;
  answer_relevancy: number | null;
  contextual_relevancy: number | null;
};

export type OnlineEvalCostSummary = {
  total: number | null;
  currency: string | null;
  priced_evaluations: number;
  unpriced_evaluations: number;
  pricing_complete: boolean;
};

export type OnlineEvalOutcomeSummary = {
  answered_successfully: number;
  safe_abstentions: number;
  failed: number;
  unclassified: number;
};

export type OnlineEvalSummary = {
  total: number;
  pending: number;
  running: number;
  completed: number;
  failed: number;
  passed: number;
  not_passed: number;
  pass_rate: number | null;
  outcomes: OnlineEvalOutcomeSummary;
  answer_success_rate: number | null;
  safe_handling_rate: number | null;
  average_scores: OnlineEvalAverageScores;
  evaluation_cost: OnlineEvalCostSummary;
};

export type OnlineEvalResultSummary = {
  id: string;
  knowledge_base_id: string | null;
  source_trace_id: string;
  status: OnlineEvalStatus;
  sample_reason: string;
  generator_provider: string | null;
  generator_model: string | null;
  faithfulness_score: number | null;
  answer_relevancy_score: number | null;
  contextual_relevancy_score: number | null;
  passed: boolean | null;
  evaluation_outcome: OnlineEvalOutcome | null;
  evaluated_at: string | null;
  created_at: string;
};

export type OnlineEvalResult = {
  id: string;
  tenant_id: string;
  knowledge_base_id: string | null;
  conversation_id: string | null;
  message_id: string | null;
  source_trace_id: string;
  status: OnlineEvalStatus;
  sample_reason: string;
  question: string;
  actual_answer: string;
  retrieval_context: string[];
  generator_provider: string | null;
  generator_model: string | null;
  faithfulness_score: number | null;
  answer_relevancy_score: number | null;
  contextual_relevancy_score: number | null;
  passed: boolean | null;
  evaluation_outcome: OnlineEvalOutcome | null;
  evaluated_at: string | null;
  error_message: string | null;
  evaluation_metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type OnlineEvalFilters = {
  knowledge_base_id?: string | null;
  status?: OnlineEvalStatus | null;
  generator_provider?: string | null;
  generator_model?: string | null;
  passed?: boolean | null;
  source_trace_id?: string | null;
  created_from?: string | null;
  created_to?: string | null;
  limit?: number;
  offset?: number;
};

export type OnlineEvalSummaryFilters = {
  knowledge_base_id?: string | null;
  generator_provider?: string | null;
  generator_model?: string | null;
  created_from?: string | null;
  created_to?: string | null;
};

export type ProcessPendingOnlineEvalRequest = {
  limit: number;
  evaluator_llm_configuration_id: string | null;
};

export type ProcessPendingOnlineEvalResponse = {
  selected: number;
  completed: number;
  failed: number;
};

export type TraceDebugSpan = {
  trace_id: string;
  span_id: string;
  parent_span_id: string | null;
  name: string;
  kind: string;
  status: string;
  start_time_unix_nano: number | null;
  end_time_unix_nano: number | null;
  duration_ms: number | null;
  attributes: Record<string, unknown>;
  resource: Record<string, unknown>;
};

export type TraceDebugTrace = {
  trace_id: string;
  span_count: number;
  spans: TraceDebugSpan[];
};
