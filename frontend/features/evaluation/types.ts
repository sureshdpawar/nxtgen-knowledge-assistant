export type EvalExpectedSource = {
  type: string;

  value: string;
};


export type EvalDataset = {
  id: string;

  knowledge_base_id: string;

  name: string;

  version: string;

  description:
    | string
    | null;
};


export type EvalDatasetImportResponse = {
  dataset: EvalDataset;

  case_count: number;
};


export type EvalCase = {
  id: string;

  dataset_id: string;

  question: string;

  expected_document_id:
    | string
    | null;

  expected_chunk_id:
    | string
    | null;

  expected_sources:
    EvalExpectedSource[];

  expected_text:
    | string
    | null;

  expected_answer:
    | string
    | null;

  answerable: boolean;
};


export type EvalExperiment = {
  id: string;

  dataset_id: string;

  knowledge_base_id: string;

  name: string;

  eval_type: string;

  top_k: number;

  chunk_size:
    | number
    | null;

  chunk_overlap:
    | number
    | null;

  embedding_model:
    | string
    | null;

  llm_model:
    | string
    | null;

  status: string;

  hit_rate:
    | number
    | null;

  mrr:
    | number
    | null;

  metrics:
    Record<
      string,
      unknown
    >;
};


export type EvalResult = {
  id: string;

  experiment_id: string;

  eval_case_id: string;

  retrieved_document_ids:
    string[];

  retrieved_chunk_ids:
    string[];

  retrieved_distances:
    number[];

  retrieval_context:
    Record<
      string,
      unknown
    >[];

  expected_rank:
    | number
    | null;

  hit_at_k:
    | boolean
    | null;

  reciprocal_rank:
    | number
    | null;

  actual_answer:
    | string
    | null;

  correctness_score:
    | number
    | null;

  faithfulness_score:
    | number
    | null;

  relevancy_score:
    | number
    | null;

  refusal_score:
    | number
    | null;

  passed:
    | boolean
    | null;

  metrics:
    Record<
      string,
      unknown
    >;

  judge_metadata:
    Record<
      string,
      unknown
    >;
};


export type RunRAGEvaluationRequest = {
  dataset_id: string;

  knowledge_base_id: string;

  name: string;

  top_k: number;

  evaluator_llm_configuration_id:
    | string
    | null;

  run_judges: boolean;
};


export type CompareEvaluationRequest = {
  baseline_experiment_id: string;

  candidate_experiment_id: string;
};


export type EvalComparisonOutcome =
  | "improved"
  | "unchanged"
  | "regressed"
  | "not_comparable";


export type EvalComparisonMetric = {
  metric: string;

  baseline:
    | number
    | null;

  candidate:
    | number
    | null;

  delta:
    | number
    | null;

  relative_delta:
    | number
    | null;

  higher_is_better: boolean;

  outcome:
    EvalComparisonOutcome;
};


export type EvalComparisonRun = {
  id: string;

  name: string;

  dataset_id: string;

  knowledge_base_id: string;

  eval_type: string;

  status: string;

  top_k: number;

  embedding_model:
    | string
    | null;

  llm_model:
    | string
    | null;

  //
  // Retrieval.
  //
  hit_rate:
    | number
    | null;

  precision_at_k:
    | number
    | null;

  recall_at_k:
    | number
    | null;

  mrr:
    | number
    | null;

  //
  // Generation.
  //
  faithfulness:
    | number
    | null;

  answer_relevancy:
    | number
    | null;

  correctness:
    | number
    | null;

  refusal_correctness:
    | number
    | null;

  pass_rate:
    | number
    | null;

  //
  // Performance.
  //
  average_retrieval_ms:
    | number
    | null;

  average_generation_ms:
    | number
    | null;

  average_rag_ms:
    | number
    | null;

  average_generation_tokens:
    | number
    | null;

  generation_tokens:
    | number
    | null;

  judge_tokens:
    | number
    | null;

  total_evaluation_tokens:
    | number
    | null;

  generator:
    | Record<
        string,
        unknown
      >
    | null;

  evaluator:
    | Record<
        string,
        unknown
      >
    | null;
};


export type EvalComparisonCaseRun = {
  eval_case_id: string;

  question:
    | string
    | null;

  answerable:
    | boolean
    | null;

  passed:
    | boolean
    | null;

  //
  // Retrieval.
  //
  hit_at_k:
    | boolean
    | null;

  expected_rank:
    | number
    | null;

  precision_at_k:
    | number
    | null;

  recall_at_k:
    | number
    | null;

  reciprocal_rank:
    | number
    | null;

  //
  // Generation.
  //
  faithfulness:
    | number
    | null;

  answer_relevancy:
    | number
    | null;

  correctness:
    | number
    | null;

  refusal_correctness:
    | number
    | null;

  //
  // Performance.
  //
  retrieval_ms:
    | number
    | null;

  generation_ms:
    | number
    | null;

  total_ms:
    | number
    | null;

  prompt_tokens:
    | number
    | null;

  completion_tokens:
    | number
    | null;

  total_tokens:
    | number
    | null;

  actual_answer:
    | string
    | null;
};


export type EvalComparisonDimension = {
  outcome:
    EvalComparisonOutcome;

  metrics:
    EvalComparisonMetric[];
};


export type EvalComparisonCaseDimensions = {
  retrieval:
    EvalComparisonDimension;

  generation:
    EvalComparisonDimension;

  performance:
    EvalComparisonDimension;
};


export type EvalComparisonCase = {
  eval_case_id: string;

  question:
    | string
    | null;

  answerable:
    | boolean
    | null;

  //
  // "outcome" is retained by the backend
  // for backward compatibility.
  //
  outcome:
    EvalComparisonOutcome;

  overall_outcome:
    EvalComparisonOutcome;

  retrieval_outcome:
    EvalComparisonOutcome;

  generation_outcome:
    EvalComparisonOutcome;

  performance_outcome:
    EvalComparisonOutcome;

  dimensions:
    EvalComparisonCaseDimensions;

  baseline:
    EvalComparisonCaseRun;

  candidate:
    EvalComparisonCaseRun;
};


export type EvalComparisonOverall = {
  outcome:
    EvalComparisonOutcome;

  retrieval_outcome:
    EvalComparisonOutcome;

  generation_outcome:
    EvalComparisonOutcome;

  performance_outcome:
    EvalComparisonOutcome;
};


export type EvalComparisonMetricGroups = {
  retrieval:
    EvalComparisonDimension;

  generation:
    EvalComparisonDimension;

  performance:
    EvalComparisonDimension;
};


export type EvalComparisonSummary = {
  overall_outcome:
    EvalComparisonOutcome;

  retrieval_outcome:
    EvalComparisonOutcome;

  generation_outcome:
    EvalComparisonOutcome;

  performance_outcome:
    EvalComparisonOutcome;

  improved_metric_count: number;

  regressed_metric_count: number;

  unchanged_metric_count: number;

  not_comparable_metric_count: number;

  improved_case_count: number;

  regressed_case_count: number;

  unchanged_case_count: number;

  not_comparable_case_count: number;

  retrieval_regressed_case_count:
    number;

  generation_regressed_case_count:
    number;

  performance_regressed_case_count:
    number;

  compared_case_count: number;
};


export type EvalComparison = {
  baseline:
    EvalComparisonRun;

  candidate:
    EvalComparisonRun;

  overall:
    EvalComparisonOverall;

  summary:
    EvalComparisonSummary;

  //
  // New dimension-based representation.
  //
  metric_groups:
    EvalComparisonMetricGroups;

  //
  // Flat metric list retained for
  // backward compatibility.
  //
  metrics:
    EvalComparisonMetric[];

  //
  // Complete comparison set.
  //
  cases:
    EvalComparisonCase[];

  improved_cases:
    EvalComparisonCase[];

  regressed_cases:
    EvalComparisonCase[];

  unchanged_cases:
    EvalComparisonCase[];

  not_comparable_cases:
    EvalComparisonCase[];
};