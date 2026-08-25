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

    def __init__(self):
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
        data: dict,
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
                experiment.knowledge_base_id,

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

            "hit_rate":
                experiment.hit_rate,

            "mrr":
                experiment.mrr,

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

            "average_rag_ms":
                self._get_nested_value(
                    metrics,
                    [
                        "latency",
                        "average_rag_ms",
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

    def _numeric_delta(
        self,
        baseline,
        candidate,
    ):
        if (
            baseline is None
            or candidate is None
        ):
            return None

        try:
            return round(
                float(
                    candidate
                )
                - float(
                    baseline
                ),
                4,
            )

        except (
            TypeError,
            ValueError,
        ):
            return None

    def _metric_comparison(
        self,
        metric_name: str,
        baseline,
        candidate,
        higher_is_better: bool,
    ) -> dict:
        delta = (
            self._numeric_delta(
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

        elif abs(
            delta
        ) < 0.0001:
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

            "higher_is_better":
                higher_is_better,

            "outcome":
                outcome,
        }

    def _case_quality_score(
        self,
        result:
            EvalResult,
    ) -> float | None:
        """
        Produce a comparison-only case score.

        This is NOT a Knowgentiq product
        "AI quality score".

        It exists only to determine whether
        an individual case generally improved
        or regressed when its pass/fail state
        did not change.

        We average only available quality
        metrics.
        """

        scores = []

        if (
            result.reciprocal_rank
            is not None
        ):
            scores.append(
                float(
                    result
                    .reciprocal_rank
                )
            )

        if (
            result.faithfulness_score
            is not None
        ):
            scores.append(
                float(
                    result
                    .faithfulness_score
                )
            )

        if (
            result.relevancy_score
            is not None
        ):
            scores.append(
                float(
                    result
                    .relevancy_score
                )
            )

        if (
            result.correctness_score
            is not None
        ):
            scores.append(
                float(
                    result
                    .correctness_score
                )
            )

        if (
            result.refusal_score
            is not None
        ):
            scores.append(
                float(
                    result
                    .refusal_score
                )
            )

        if not scores:
            return None

        return round(
            sum(
                scores
            )
            / len(
                scores
            ),
            4,
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

            "hit_at_k":
                result.hit_at_k,

            "expected_rank":
                result.expected_rank,

            "reciprocal_rank":
                result.reciprocal_rank,

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

            "quality_score":
                self._case_quality_score(
                    result
                ),

            "actual_answer":
                result.actual_answer,
        }

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

        baseline_score = (
            baseline_data[
                "quality_score"
            ]
        )

        candidate_score = (
            candidate_data[
                "quality_score"
            ]
        )

        quality_delta = (
            self._numeric_delta(
                baseline=
                    baseline_score,

                candidate=
                    candidate_score,
            )
        )

        #
        # Pass transition has priority.
        #
        if (
            baseline.passed
            is False
            and candidate.passed
            is True
        ):
            outcome = (
                "improved"
            )

        elif (
            baseline.passed
            is True
            and candidate.passed
            is False
        ):
            outcome = (
                "regressed"
            )

        elif quality_delta is None:
            outcome = (
                "unchanged"
            )

        elif quality_delta > 0.001:
            outcome = (
                "improved"
            )

        elif quality_delta < -0.001:
            outcome = (
                "regressed"
            )

        else:
            outcome = (
                "unchanged"
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

            "outcome":
                outcome,

            "quality_delta":
                quality_delta,

            "baseline":
                baseline_data,

            "candidate":
                candidate_data,
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
                "be completed before comparison."
            )

        #
        # V1 comparisons intentionally require
        # the same golden dataset.
        #
        # This guarantees case-to-case alignment.
        #
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

        metric_definitions = [
            (
                "hit_rate",
                True,
            ),
            (
                "mrr",
                True,
            ),
            (
                "faithfulness",
                True,
            ),
            (
                "answer_relevancy",
                True,
            ),
            (
                "correctness",
                True,
            ),
            (
                "refusal_correctness",
                True,
            ),
            (
                "pass_rate",
                True,
            ),
            (
                "average_rag_ms",
                False,
            ),
            (
                "generation_tokens",
                False,
            ),
            (
                "judge_tokens",
                False,
            ),
            (
                "total_evaluation_tokens",
                False,
            ),
        ]

        metric_comparisons = []

        for (
            metric_name,
            higher_is_better,
        ) in metric_definitions:
            metric_comparisons.append(
                self._metric_comparison(
                    metric_name=
                        metric_name,

                    baseline=
                        baseline_summary.get(
                            metric_name
                        ),

                    candidate=
                        candidate_summary.get(
                            metric_name
                        ),

                    higher_is_better=
                        higher_is_better,
                )
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
        # Stable order for UI.
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
                    "outcome"
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
                    "outcome"
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
                    "outcome"
                ]
                == "unchanged"
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

        return {
            "baseline":
                baseline_summary,

            "candidate":
                candidate_summary,

            "summary": {
                "improved_metric_count":
                    improved_metrics,

                "regressed_metric_count":
                    regressed_metrics,

                "unchanged_metric_count":
                    unchanged_metrics,

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

                "compared_case_count":
                    len(
                        case_comparisons
                    ),
            },

            "metrics":
                metric_comparisons,

            "improved_cases":
                improved_cases,

            "regressed_cases":
                regressed_cases,

            "unchanged_cases":
                unchanged_cases,
        }