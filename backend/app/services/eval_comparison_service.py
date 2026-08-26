from uuid import UUID

from sqlalchemy.orm import Session

from app.models.eval_case import (
    EvalCase,
)
from app.models.eval_experiment import (
    EvalExperiment,
)
from app.models.eval_result import (
    EvalResult,
)
from app.repositories.eval_experiment_repository import (
    EvalExperimentRepository,
)
from app.repositories.eval_result_repository import (
    EvalResultRepository,
)


class EvalComparisonService:

    #
    # Small changes below these values are
    # treated as unchanged.
    #
    SCORE_TOLERANCE = 0.001

    LATENCY_TOLERANCE_RATIO = 0.05

    TOKEN_TOLERANCE_RATIO = 0.05

    def __init__(
        self,
    ):
        self.experiment_repository = (
            EvalExperimentRepository()
        )

        self.result_repository = (
            EvalResultRepository()
        )

    def _get_experiment(
        self,
        db: Session,
        experiment_id: UUID,
    ) -> EvalExperiment:
        experiment = (
            self.experiment_repository
            .get(
                db=db,

                entity_id=
                    experiment_id,
            )
        )

        if experiment is None:
            raise ValueError(
                "Evaluation run not found."
            )

        return experiment

    def _get_nested_value(
        self,
        data: dict | None,
        path: list[str],
    ):
        current = (
            data
            or {}
        )

        for key in path:
            if not isinstance(
                current,
                dict,
            ):
                return None

            current = (
                current.get(
                    key
                )
            )

            if current is None:
                return None

        return current

    def _to_float(
        self,
        value,
    ) -> float | None:
        if value is None:
            return None

        try:
            return float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):
            return None

    def _numeric_delta(
        self,
        baseline,
        candidate,
    ) -> float | None:
        baseline_value = (
            self._to_float(
                baseline
            )
        )

        candidate_value = (
            self._to_float(
                candidate
            )
        )

        if (
            baseline_value is None
            or candidate_value is None
        ):
            return None

        return round(
            candidate_value
            - baseline_value,
            6,
        )

    def _relative_delta(
        self,
        baseline,
        candidate,
    ) -> float | None:
        baseline_value = (
            self._to_float(
                baseline
            )
        )

        candidate_value = (
            self._to_float(
                candidate
            )
        )

        if (
            baseline_value is None
            or candidate_value is None
        ):
            return None

        if baseline_value == 0:
            if candidate_value == 0:
                return 0.0

            return None

        return round(
            (
                candidate_value
                - baseline_value
            )
            / abs(
                baseline_value
            ),
            6,
        )

    def _metric_comparison(
        self,
        metric_name: str,
        baseline,
        candidate,
        higher_is_better: bool,
        tolerance: float = 0.001,
        relative_tolerance:
            float | None = None,
    ) -> dict:
        delta = (
            self._numeric_delta(
                baseline=
                    baseline,

                candidate=
                    candidate,
            )
        )

        relative_delta = (
            self._relative_delta(
                baseline=
                    baseline,

                candidate=
                    candidate,
            )
        )

        if delta is None:
            outcome = (
                "not_comparable"
            )

        else:
            if (
                relative_tolerance
                is not None
                and relative_delta
                is not None
            ):
                unchanged = (
                    abs(
                        relative_delta
                    )
                    <= relative_tolerance
                )

            else:
                unchanged = (
                    abs(
                        delta
                    )
                    <= tolerance
                )

            if unchanged:
                outcome = (
                    "unchanged"
                )

            elif higher_is_better:
                outcome = (
                    "improved"
                    if delta > 0
                    else "regressed"
                )

            else:
                outcome = (
                    "improved"
                    if delta < 0
                    else "regressed"
                )

        return {
            "metric":
                metric_name,

            "baseline":
                baseline,

            "candidate":
                candidate,

            "delta":
                delta,

            "relative_delta":
                relative_delta,

            "higher_is_better":
                higher_is_better,

            "outcome":
                outcome,
        }

    def _run_summary(
        self,
        experiment:
            EvalExperiment,
    ) -> dict:
        metrics = (
            experiment.metrics
            or {}
        )

        return {
            "id":
                experiment.id,

            "name":
                experiment.name,

            "dataset_id":
                experiment.dataset_id,

            "knowledge_base_id":
                experiment
                .knowledge_base_id,

            "eval_type":
                experiment.eval_type,

            "status":
                experiment.status,

            "top_k":
                experiment.top_k,

            "embedding_model":
                experiment.embedding_model,

            "llm_model":
                experiment.llm_model,

            #
            # Retrieval.
            #
            "hit_rate":
                self._get_nested_value(
                    metrics,
                    [
                        "retrieval",
                        "hit_rate",
                    ],
                )
                if self._get_nested_value(
                    metrics,
                    [
                        "retrieval",
                        "hit_rate",
                    ],
                )
                is not None
                else experiment.hit_rate,

            "precision_at_k":
                self._get_nested_value(
                    metrics,
                    [
                        "retrieval",
                        "precision_at_k",
                    ],
                ),

            "recall_at_k":
                self._get_nested_value(
                    metrics,
                    [
                        "retrieval",
                        "recall_at_k",
                    ],
                ),

            "mrr":
                self._get_nested_value(
                    metrics,
                    [
                        "retrieval",
                        "mrr",
                    ],
                )
                if self._get_nested_value(
                    metrics,
                    [
                        "retrieval",
                        "mrr",
                    ],
                )
                is not None
                else experiment.mrr,

            #
            # Generation.
            #
            "faithfulness":
                self._get_nested_value(
                    metrics,
                    [
                        "generation",
                        "faithfulness",
                        "average_score",
                    ],
                ),

            "answer_relevancy":
                self._get_nested_value(
                    metrics,
                    [
                        "generation",
                        "answer_relevancy",
                        "average_score",
                    ],
                ),

            "correctness":
                self._get_nested_value(
                    metrics,
                    [
                        "generation",
                        "correctness",
                        "average_score",
                    ],
                ),

            "refusal_correctness":
                self._get_nested_value(
                    metrics,
                    [
                        "generation",
                        "refusal_correctness",
                        "average_score",
                    ],
                ),

            "pass_rate":
                self._get_nested_value(
                    metrics,
                    [
                        "cases",
                        "pass_rate",
                    ],
                ),

            #
            # Performance.
            #
            "average_retrieval_ms":
                self._get_nested_value(
                    metrics,
                    [
                        "latency",
                        "average_retrieval_ms",
                    ],
                ),

            "average_generation_ms":
                self._get_nested_value(
                    metrics,
                    [
                        "latency",
                        "average_generation_ms",
                    ],
                ),

            "average_rag_ms":
                self._get_nested_value(
                    metrics,
                    [
                        "latency",
                        "average_rag_ms",
                    ],
                ),

            "average_generation_tokens":
                self._get_nested_value(
                    metrics,
                    [
                        "usage",
                        "generation",
                        "average_tokens_per_case",
                    ],
                ),

            "generation_tokens":
                self._get_nested_value(
                    metrics,
                    [
                        "usage",
                        "generation",
                        "total_tokens",
                    ],
                ),

            "judge_tokens":
                self._get_nested_value(
                    metrics,
                    [
                        "usage",
                        "judge",
                        "total_tokens",
                    ],
                ),

            "total_evaluation_tokens":
                self._get_nested_value(
                    metrics,
                    [
                        "usage",
                        "total_evaluation_tokens",
                    ],
                ),

            "generator":
                metrics.get(
                    "generator"
                ),

            "evaluator":
                metrics.get(
                    "evaluator"
                ),
        }

    def _metric_score_from_result(
        self,
        result: EvalResult,
        metric_name: str,
    ) -> float | None:
        metrics = (
            result.metrics
            or {}
        )

        metric = (
            metrics.get(
                metric_name
            )
        )

        if isinstance(
            metric,
            dict,
        ):
            return self._to_float(
                metric.get(
                    "score"
                )
            )

        return None

    def _latency_from_result(
        self,
        result: EvalResult,
        metric_name: str,
    ) -> float | None:
        metrics = (
            result.metrics
            or {}
        )

        latency = (
            metrics.get(
                "latency"
            )
            or {}
        )

        if not isinstance(
            latency,
            dict,
        ):
            return None

        return self._to_float(
            latency.get(
                metric_name
            )
        )

    def _tokens_from_result(
        self,
        result: EvalResult,
        metric_name: str,
    ) -> float | None:
        metrics = (
            result.metrics
            or {}
        )

        usage = (
            metrics.get(
                "token_usage"
            )
            or {}
        )

        if not isinstance(
            usage,
            dict,
        ):
            return None

        return self._to_float(
            usage.get(
                metric_name
            )
        )

    def _result_to_case_summary(
        self,
        db: Session,
        result:
            EvalResult,
    ) -> dict:
        eval_case = db.get(
            EvalCase,
            result.eval_case_id,
        )

        precision_at_k = (
            self._metric_score_from_result(
                result=
                    result,

                metric_name=
                    "precision_at_k",
            )
        )

        recall_at_k = (
            self._metric_score_from_result(
                result=
                    result,

                metric_name=
                    "recall_at_k",
            )
        )

        return {
            "eval_case_id":
                result.eval_case_id,

            "question":
                (
                    eval_case.question
                    if eval_case
                    is not None
                    else None
                ),

            "answerable":
                (
                    eval_case.answerable
                    if eval_case
                    is not None
                    else None
                ),

            "passed":
                result.passed,

            #
            # Retrieval.
            #
            "hit_at_k":
                result.hit_at_k,

            "expected_rank":
                result.expected_rank,

            "precision_at_k":
                precision_at_k,

            "recall_at_k":
                recall_at_k,

            "reciprocal_rank":
                result.reciprocal_rank,

            #
            # Generation.
            #
            "faithfulness":
                result
                .faithfulness_score,

            "answer_relevancy":
                result
                .relevancy_score,

            "correctness":
                result
                .correctness_score,

            "refusal_correctness":
                result
                .refusal_score,

            #
            # Performance.
            #
            "retrieval_ms":
                self._latency_from_result(
                    result=
                        result,

                    metric_name=
                        "retrieval_ms",
                ),

            "generation_ms":
                self._latency_from_result(
                    result=
                        result,

                    metric_name=
                        "generation_ms",
                ),

            "total_ms":
                self._latency_from_result(
                    result=
                        result,

                    metric_name=
                        "total_ms",
                ),

            "prompt_tokens":
                self._tokens_from_result(
                    result=
                        result,

                    metric_name=
                        "prompt_tokens",
                ),

            "completion_tokens":
                self._tokens_from_result(
                    result=
                        result,

                    metric_name=
                        "completion_tokens",
                ),

            "total_tokens":
                self._tokens_from_result(
                    result=
                        result,

                    metric_name=
                        "total_tokens",
                ),

            "actual_answer":
                result.actual_answer,
        }

    def _outcome_from_metrics(
        self,
        comparisons: list[dict],
    ) -> str:
        comparable = [
            item
            for item
            in comparisons
            if (
                item.get(
                    "outcome"
                )
                != "not_comparable"
            )
        ]

        if not comparable:
            return (
                "not_comparable"
            )

        has_regression = any(
            item.get(
                "outcome"
            )
            == "regressed"
            for item
            in comparable
        )

        has_improvement = any(
            item.get(
                "outcome"
            )
            == "improved"
            for item
            in comparable
        )

        #
        # Conservative policy:
        #
        # Any regression inside a dimension
        # marks that dimension regressed.
        #
        # Otherwise any improvement marks it
        # improved.
        #
        if has_regression:
            return (
                "regressed"
            )

        if has_improvement:
            return (
                "improved"
            )

        return (
            "unchanged"
        )

    def _overall_outcome(
        self,
        retrieval_outcome: str,
        generation_outcome: str,
        performance_outcome: str,
    ) -> str:
        quality_outcomes = [
            outcome
            for outcome
            in (
                retrieval_outcome,
                generation_outcome,
            )
            if outcome
            != "not_comparable"
        ]

        #
        # Quality regressions have priority.
        #
        if (
            "regressed"
            in quality_outcomes
        ):
            return (
                "regressed"
            )

        #
        # If retrieval/generation quality
        # improved and neither quality
        # dimension regressed, the overall
        # result improved.
        #
        if (
            "improved"
            in quality_outcomes
        ):
            return (
                "improved"
            )

        #
        # When quality is unchanged, use
        # performance as the tie-breaker.
        #
        if (
            performance_outcome
            == "regressed"
        ):
            return (
                "regressed"
            )

        if (
            performance_outcome
            == "improved"
        ):
            return (
                "improved"
            )

        if quality_outcomes:
            return (
                "unchanged"
            )

        if (
            performance_outcome
            != "not_comparable"
        ):
            return (
                performance_outcome
            )

        return (
            "not_comparable"
        )

    def _compare_case(
        self,
        db: Session,
        baseline:
            EvalResult,
        candidate:
            EvalResult,
    ) -> dict:
        baseline_data = (
            self._result_to_case_summary(
                db=db,

                result=
                    baseline,
            )
        )

        candidate_data = (
            self._result_to_case_summary(
                db=db,

                result=
                    candidate,
            )
        )

        #
        # Retrieval.
        #
        retrieval_metrics = [
            self._metric_comparison(
                metric_name=
                    "hit_at_k",

                baseline=(
                    1.0
                    if baseline_data[
                        "hit_at_k"
                    ]
                    is True
                    else (
                        0.0
                        if baseline_data[
                            "hit_at_k"
                        ]
                        is False
                        else None
                    )
                ),

                candidate=(
                    1.0
                    if candidate_data[
                        "hit_at_k"
                    ]
                    is True
                    else (
                        0.0
                        if candidate_data[
                            "hit_at_k"
                        ]
                        is False
                        else None
                    )
                ),

                higher_is_better=
                    True,

                tolerance=
                    0.0,
            ),

            self._metric_comparison(
                metric_name=
                    "precision_at_k",

                baseline=
                    baseline_data[
                        "precision_at_k"
                    ],

                candidate=
                    candidate_data[
                        "precision_at_k"
                    ],

                higher_is_better=
                    True,

                tolerance=
                    self
                    .SCORE_TOLERANCE,
            ),

            self._metric_comparison(
                metric_name=
                    "recall_at_k",

                baseline=
                    baseline_data[
                        "recall_at_k"
                    ],

                candidate=
                    candidate_data[
                        "recall_at_k"
                    ],

                higher_is_better=
                    True,

                tolerance=
                    self
                    .SCORE_TOLERANCE,
            ),

            self._metric_comparison(
                metric_name=
                    "reciprocal_rank",

                baseline=
                    baseline_data[
                        "reciprocal_rank"
                    ],

                candidate=
                    candidate_data[
                        "reciprocal_rank"
                    ],

                higher_is_better=
                    True,

                tolerance=
                    self
                    .SCORE_TOLERANCE,
            ),
        ]

        retrieval_outcome = (
            self._outcome_from_metrics(
                retrieval_metrics
            )
        )

        #
        # Generation.
        #
        generation_metrics = [
            self._metric_comparison(
                metric_name=
                    "faithfulness",

                baseline=
                    baseline_data[
                        "faithfulness"
                    ],

                candidate=
                    candidate_data[
                        "faithfulness"
                    ],

                higher_is_better=
                    True,

                tolerance=
                    self
                    .SCORE_TOLERANCE,
            ),

            self._metric_comparison(
                metric_name=
                    "answer_relevancy",

                baseline=
                    baseline_data[
                        "answer_relevancy"
                    ],

                candidate=
                    candidate_data[
                        "answer_relevancy"
                    ],

                higher_is_better=
                    True,

                tolerance=
                    self
                    .SCORE_TOLERANCE,
            ),

            self._metric_comparison(
                metric_name=
                    "correctness",

                baseline=
                    baseline_data[
                        "correctness"
                    ],

                candidate=
                    candidate_data[
                        "correctness"
                    ],

                higher_is_better=
                    True,

                tolerance=
                    self
                    .SCORE_TOLERANCE,
            ),

            self._metric_comparison(
                metric_name=
                    "refusal_correctness",

                baseline=
                    baseline_data[
                        "refusal_correctness"
                    ],

                candidate=
                    candidate_data[
                        "refusal_correctness"
                    ],

                higher_is_better=
                    True,

                tolerance=
                    self
                    .SCORE_TOLERANCE,
            ),
        ]

        generation_outcome = (
            self._outcome_from_metrics(
                generation_metrics
            )
        )

        #
        # Performance.
        #
        performance_metrics = [
            self._metric_comparison(
                metric_name=
                    "retrieval_ms",

                baseline=
                    baseline_data[
                        "retrieval_ms"
                    ],

                candidate=
                    candidate_data[
                        "retrieval_ms"
                    ],

                higher_is_better=
                    False,

                relative_tolerance=
                    self
                    .LATENCY_TOLERANCE_RATIO,
            ),

            self._metric_comparison(
                metric_name=
                    "generation_ms",

                baseline=
                    baseline_data[
                        "generation_ms"
                    ],

                candidate=
                    candidate_data[
                        "generation_ms"
                    ],

                higher_is_better=
                    False,

                relative_tolerance=
                    self
                    .LATENCY_TOLERANCE_RATIO,
            ),

            self._metric_comparison(
                metric_name=
                    "total_ms",

                baseline=
                    baseline_data[
                        "total_ms"
                    ],

                candidate=
                    candidate_data[
                        "total_ms"
                    ],

                higher_is_better=
                    False,

                relative_tolerance=
                    self
                    .LATENCY_TOLERANCE_RATIO,
            ),

            self._metric_comparison(
                metric_name=
                    "total_tokens",

                baseline=
                    baseline_data[
                        "total_tokens"
                    ],

                candidate=
                    candidate_data[
                        "total_tokens"
                    ],

                higher_is_better=
                    False,

                relative_tolerance=
                    self
                    .TOKEN_TOLERANCE_RATIO,
            ),
        ]

        performance_outcome = (
            self._outcome_from_metrics(
                performance_metrics
            )
        )

        overall_outcome = (
            self._overall_outcome(
                retrieval_outcome=
                    retrieval_outcome,

                generation_outcome=
                    generation_outcome,

                performance_outcome=
                    performance_outcome,
            )
        )

        return {
            "eval_case_id":
                baseline.eval_case_id,

            "question":
                baseline_data[
                    "question"
                ],

            "answerable":
                baseline_data[
                    "answerable"
                ],

            #
            # Backward-compatible field.
            #
            "outcome":
                overall_outcome,

            "overall_outcome":
                overall_outcome,

            "retrieval_outcome":
                retrieval_outcome,

            "generation_outcome":
                generation_outcome,

            "performance_outcome":
                performance_outcome,

            "dimensions": {
                "retrieval": {
                    "outcome":
                        retrieval_outcome,

                    "metrics":
                        retrieval_metrics,
                },

                "generation": {
                    "outcome":
                        generation_outcome,

                    "metrics":
                        generation_metrics,
                },

                "performance": {
                    "outcome":
                        performance_outcome,

                    "metrics":
                        performance_metrics,
                },
            },

            "baseline":
                baseline_data,

            "candidate":
                candidate_data,
        }

    def _build_run_metric_comparisons(
        self,
        baseline: dict,
        candidate: dict,
    ) -> dict:
        retrieval = [
            self._metric_comparison(
                metric_name=
                    "hit_rate",

                baseline=
                    baseline.get(
                        "hit_rate"
                    ),

                candidate=
                    candidate.get(
                        "hit_rate"
                    ),

                higher_is_better=
                    True,
            ),

            self._metric_comparison(
                metric_name=
                    "precision_at_k",

                baseline=
                    baseline.get(
                        "precision_at_k"
                    ),

                candidate=
                    candidate.get(
                        "precision_at_k"
                    ),

                higher_is_better=
                    True,
            ),

            self._metric_comparison(
                metric_name=
                    "recall_at_k",

                baseline=
                    baseline.get(
                        "recall_at_k"
                    ),

                candidate=
                    candidate.get(
                        "recall_at_k"
                    ),

                higher_is_better=
                    True,
            ),

            self._metric_comparison(
                metric_name=
                    "mrr",

                baseline=
                    baseline.get(
                        "mrr"
                    ),

                candidate=
                    candidate.get(
                        "mrr"
                    ),

                higher_is_better=
                    True,
            ),
        ]

        generation = [
            self._metric_comparison(
                metric_name=
                    "faithfulness",

                baseline=
                    baseline.get(
                        "faithfulness"
                    ),

                candidate=
                    candidate.get(
                        "faithfulness"
                    ),

                higher_is_better=
                    True,
            ),

            self._metric_comparison(
                metric_name=
                    "answer_relevancy",

                baseline=
                    baseline.get(
                        "answer_relevancy"
                    ),

                candidate=
                    candidate.get(
                        "answer_relevancy"
                    ),

                higher_is_better=
                    True,
            ),

            self._metric_comparison(
                metric_name=
                    "correctness",

                baseline=
                    baseline.get(
                        "correctness"
                    ),

                candidate=
                    candidate.get(
                        "correctness"
                    ),

                higher_is_better=
                    True,
            ),

            self._metric_comparison(
                metric_name=
                    "refusal_correctness",

                baseline=
                    baseline.get(
                        "refusal_correctness"
                    ),

                candidate=
                    candidate.get(
                        "refusal_correctness"
                    ),

                higher_is_better=
                    True,
            ),

            self._metric_comparison(
                metric_name=
                    "pass_rate",

                baseline=
                    baseline.get(
                        "pass_rate"
                    ),

                candidate=
                    candidate.get(
                        "pass_rate"
                    ),

                higher_is_better=
                    True,
            ),
        ]

        performance = [
            self._metric_comparison(
                metric_name=
                    "average_retrieval_ms",

                baseline=
                    baseline.get(
                        "average_retrieval_ms"
                    ),

                candidate=
                    candidate.get(
                        "average_retrieval_ms"
                    ),

                higher_is_better=
                    False,

                relative_tolerance=
                    self
                    .LATENCY_TOLERANCE_RATIO,
            ),

            self._metric_comparison(
                metric_name=
                    "average_generation_ms",

                baseline=
                    baseline.get(
                        "average_generation_ms"
                    ),

                candidate=
                    candidate.get(
                        "average_generation_ms"
                    ),

                higher_is_better=
                    False,

                relative_tolerance=
                    self
                    .LATENCY_TOLERANCE_RATIO,
            ),

            self._metric_comparison(
                metric_name=
                    "average_rag_ms",

                baseline=
                    baseline.get(
                        "average_rag_ms"
                    ),

                candidate=
                    candidate.get(
                        "average_rag_ms"
                    ),

                higher_is_better=
                    False,

                relative_tolerance=
                    self
                    .LATENCY_TOLERANCE_RATIO,
            ),

            self._metric_comparison(
                metric_name=
                    "average_generation_tokens",

                baseline=
                    baseline.get(
                        "average_generation_tokens"
                    ),

                candidate=
                    candidate.get(
                        "average_generation_tokens"
                    ),

                higher_is_better=
                    False,

                relative_tolerance=
                    self
                    .TOKEN_TOLERANCE_RATIO,
            ),
        ]

        return {
            "retrieval":
                retrieval,

            "generation":
                generation,

            "performance":
                performance,
        }

    def compare(
        self,
        db: Session,
        baseline_experiment_id: UUID,
        candidate_experiment_id: UUID,
    ) -> dict:
        if (
            baseline_experiment_id
            == candidate_experiment_id
        ):
            raise ValueError(
                "Baseline and candidate "
                "runs must be different."
            )

        baseline = (
            self._get_experiment(
                db=db,

                experiment_id=
                    baseline_experiment_id,
            )
        )

        candidate = (
            self._get_experiment(
                db=db,

                experiment_id=
                    candidate_experiment_id,
            )
        )

        if (
            baseline.status
            != "completed"
            or candidate.status
            != "completed"
        ):
            raise ValueError(
                "Both evaluation runs must "
                "be completed before "
                "comparison."
            )

        if (
            baseline.dataset_id
            != candidate.dataset_id
        ):
            raise ValueError(
                "Baseline and candidate runs "
                "must use the same evaluation "
                "dataset."
            )

        if (
            baseline.knowledge_base_id
            != candidate.knowledge_base_id
        ):
            raise ValueError(
                "Baseline and candidate runs "
                "must evaluate the same "
                "Knowledge Base."
            )

        if (
            baseline.eval_type
            != candidate.eval_type
        ):
            raise ValueError(
                "Baseline and candidate runs "
                "must have the same evaluation "
                "type."
            )

        baseline_summary = (
            self._run_summary(
                baseline
            )
        )

        candidate_summary = (
            self._run_summary(
                candidate
            )
        )

        #
        # Run-level metric comparison.
        #
        metric_groups = (
            self
            ._build_run_metric_comparisons(
                baseline=
                    baseline_summary,

                candidate=
                    candidate_summary,
            )
        )

        retrieval_outcome = (
            self._outcome_from_metrics(
                metric_groups[
                    "retrieval"
                ]
            )
        )

        generation_outcome = (
            self._outcome_from_metrics(
                metric_groups[
                    "generation"
                ]
            )
        )

        performance_outcome = (
            self._outcome_from_metrics(
                metric_groups[
                    "performance"
                ]
            )
        )

        overall_outcome = (
            self._overall_outcome(
                retrieval_outcome=
                    retrieval_outcome,

                generation_outcome=
                    generation_outcome,

                performance_outcome=
                    performance_outcome,
            )
        )

        #
        # Flat metric list retained for
        # backward compatibility with the UI.
        #
        metric_comparisons = (
            metric_groups[
                "retrieval"
            ]
            + metric_groups[
                "generation"
            ]
            + metric_groups[
                "performance"
            ]
        )

        baseline_results = (
            self.result_repository
            .list_by_experiment_id(
                db=db,

                experiment_id=
                    baseline.id,
            )
        )

        candidate_results = (
            self.result_repository
            .list_by_experiment_id(
                db=db,

                experiment_id=
                    candidate.id,
            )
        )

        baseline_by_case = {
            result.eval_case_id:
                result

            for result
            in baseline_results
        }

        candidate_by_case = {
            result.eval_case_id:
                result

            for result
            in candidate_results
        }

        common_case_ids = (
            set(
                baseline_by_case.keys()
            )
            & set(
                candidate_by_case.keys()
            )
        )

        case_comparisons = []

        for case_id in common_case_ids:
            case_comparisons.append(
                self._compare_case(
                    db=db,

                    baseline=
                        baseline_by_case[
                            case_id
                        ],

                    candidate=
                        candidate_by_case[
                            case_id
                        ],
                )
            )

        #
        # Stable ordering for the UI.
        #
        case_comparisons.sort(
            key=lambda item: (
                item[
                    "question"
                ]
                or ""
            )
        )

        improved_cases = [
            item
            for item
            in case_comparisons
            if (
                item[
                    "overall_outcome"
                ]
                == "improved"
            )
        ]

        regressed_cases = [
            item
            for item
            in case_comparisons
            if (
                item[
                    "overall_outcome"
                ]
                == "regressed"
            )
        ]

        unchanged_cases = [
            item
            for item
            in case_comparisons
            if (
                item[
                    "overall_outcome"
                ]
                == "unchanged"
            )
        ]

        not_comparable_cases = [
            item
            for item
            in case_comparisons
            if (
                item[
                    "overall_outcome"
                ]
                == "not_comparable"
            )
        ]

        improved_metrics = sum(
            1
            for item
            in metric_comparisons
            if (
                item[
                    "outcome"
                ]
                == "improved"
            )
        )

        regressed_metrics = sum(
            1
            for item
            in metric_comparisons
            if (
                item[
                    "outcome"
                ]
                == "regressed"
            )
        )

        unchanged_metrics = sum(
            1
            for item
            in metric_comparisons
            if (
                item[
                    "outcome"
                ]
                == "unchanged"
            )
        )

        not_comparable_metrics = sum(
            1
            for item
            in metric_comparisons
            if (
                item[
                    "outcome"
                ]
                == "not_comparable"
            )
        )

        retrieval_regressed_cases = sum(
            1
            for item
            in case_comparisons
            if (
                item[
                    "retrieval_outcome"
                ]
                == "regressed"
            )
        )

        generation_regressed_cases = sum(
            1
            for item
            in case_comparisons
            if (
                item[
                    "generation_outcome"
                ]
                == "regressed"
            )
        )

        performance_regressed_cases = sum(
            1
            for item
            in case_comparisons
            if (
                item[
                    "performance_outcome"
                ]
                == "regressed"
            )
        )

        return {
            "baseline":
                baseline_summary,

            "candidate":
                candidate_summary,

            "overall": {
                "outcome":
                    overall_outcome,

                "retrieval_outcome":
                    retrieval_outcome,

                "generation_outcome":
                    generation_outcome,

                "performance_outcome":
                    performance_outcome,
            },

            "summary": {
                "overall_outcome":
                    overall_outcome,

                "retrieval_outcome":
                    retrieval_outcome,

                "generation_outcome":
                    generation_outcome,

                "performance_outcome":
                    performance_outcome,

                "improved_metric_count":
                    improved_metrics,

                "regressed_metric_count":
                    regressed_metrics,

                "unchanged_metric_count":
                    unchanged_metrics,

                "not_comparable_metric_count":
                    not_comparable_metrics,

                "improved_case_count":
                    len(
                        improved_cases
                    ),

                "regressed_case_count":
                    len(
                        regressed_cases
                    ),

                "unchanged_case_count":
                    len(
                        unchanged_cases
                    ),

                "not_comparable_case_count":
                    len(
                        not_comparable_cases
                    ),

                "retrieval_regressed_case_count":
                    retrieval_regressed_cases,

                "generation_regressed_case_count":
                    generation_regressed_cases,

                "performance_regressed_case_count":
                    performance_regressed_cases,

                "compared_case_count":
                    len(
                        case_comparisons
                    ),
            },

            #
            # New grouped representation.
            #
            "metric_groups": {
                "retrieval": {
                    "outcome":
                        retrieval_outcome,

                    "metrics":
                        metric_groups[
                            "retrieval"
                        ],
                },

                "generation": {
                    "outcome":
                        generation_outcome,

                    "metrics":
                        metric_groups[
                            "generation"
                        ],
                },

                "performance": {
                    "outcome":
                        performance_outcome,

                    "metrics":
                        metric_groups[
                            "performance"
                        ],
                },
            },

            #
            # Backward-compatible flat list.
            #
            "metrics":
                metric_comparisons,

            "cases":
                case_comparisons,

            "improved_cases":
                improved_cases,

            "regressed_cases":
                regressed_cases,

            "unchanged_cases":
                unchanged_cases,

            "not_comparable_cases":
                not_comparable_cases,
        }