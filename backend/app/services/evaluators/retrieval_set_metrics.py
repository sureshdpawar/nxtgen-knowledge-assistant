from app.services.evaluators.base import (
    BaseEvaluator,
    EvaluationInput,
    EvaluationMetricResult,
)
from app.services.evaluators.retrieval import (
    _normalize_external_id,
    _normalize_url,
)


def _normalized_expected_sources(
    expected_sources: list,
) -> set[str]:
    values: set[str] = set()

    for source in expected_sources or []:
        if not isinstance(source, dict):
            continue

        source_type = str(
            source.get("type", "")
        ).strip().lower()
        source_value = str(
            source.get("value", "")
        ).strip()

        if not source_value:
            continue

        if source_type == "url":
            values.add(
                _normalize_url(source_value)
            )
        elif source_type == "external_id":
            values.add(
                _normalize_external_id(source_value)
            )

    return {
        value
        for value in values
        if value
    }


def _relevance_sets(
    evaluation_input: EvaluationInput,
) -> tuple[set[str], list[str], str | None]:
    metadata = evaluation_input.metadata

    expected_chunk_id = metadata.get(
        "expected_chunk_id"
    )
    expected_document_id = metadata.get(
        "expected_document_id"
    )
    expected_sources = metadata.get(
        "expected_sources",
        [],
    ) or []

    if expected_chunk_id is not None:
        expected = {
            str(expected_chunk_id)
        }
        retrieved = [
            str(value)
            for value in metadata.get(
                "retrieved_chunk_ids",
                [],
            ) or []
        ]
        return expected, retrieved, "chunk_id"

    if expected_document_id is not None:
        expected = {
            str(expected_document_id)
        }
        retrieved = [
            str(value)
            for value in metadata.get(
                "retrieved_document_ids",
                [],
            ) or []
        ]
        return expected, retrieved, "document_id"

    expected = _normalized_expected_sources(
        expected_sources
    )
    if expected:
        retrieved = [
            _normalize_external_id(str(value))
            for value in metadata.get(
                "retrieved_document_external_ids",
                [],
            ) or []
            if value
        ]
        return expected, retrieved, "expected_source"

    return set(), [], None


def _matched_relevant_count(
    expected: set[str],
    retrieved: list[str],
) -> int:
    # Count unique relevant identities. Multiple chunks from the
    # same relevant document/source must not inflate precision.
    return len(
        expected.intersection(
            set(retrieved)
        )
    )


class PrecisionAtKEvaluator(BaseEvaluator):
    """Calculate retrieval Precision@K for cases with ground truth."""

    metric_name = "precision_at_k"
    evaluator_type = "deterministic"
    evaluator_engine = "knowgentiq"

    def evaluate(
        self,
        evaluation_input: EvaluationInput,
    ) -> EvaluationMetricResult:
        expected, retrieved, matched_by = (
            _relevance_sets(evaluation_input)
        )

        if not expected:
            return EvaluationMetricResult(
                metric_name=self.metric_name,
                score=None,
                passed=None,
                reason=(
                    "No retrieval ground truth was configured "
                    "for this test case."
                ),
                evaluator_type=self.evaluator_type,
                evaluator_engine=self.evaluator_engine,
            )

        top_k = int(
            evaluation_input.metadata.get(
                "top_k",
                len(retrieved),
            )
            or len(retrieved)
            or 1
        )
        retrieved_at_k = retrieved[:top_k]
        relevant_count = _matched_relevant_count(
            expected,
            retrieved_at_k,
        )

        # Precision@K uses K as the denominator. This penalizes a
        # retriever that returns irrelevant slots in the requested K.
        score = relevant_count / float(top_k)

        return EvaluationMetricResult(
            metric_name=self.metric_name,
            score=score,
            passed=None,
            reason=(
                f"{relevant_count} unique relevant source(s) "
                f"were found in the requested top {top_k}."
            ),
            evaluator_type=self.evaluator_type,
            evaluator_engine=self.evaluator_engine,
            metadata={
                "top_k": top_k,
                "relevant_retrieved_count": relevant_count,
                "expected_relevant_count": len(expected),
                "matched_by": matched_by,
            },
        )


class RecallAtKEvaluator(BaseEvaluator):
    """Calculate retrieval Recall@K for cases with ground truth."""

    metric_name = "recall_at_k"
    evaluator_type = "deterministic"
    evaluator_engine = "knowgentiq"

    def evaluate(
        self,
        evaluation_input: EvaluationInput,
    ) -> EvaluationMetricResult:
        expected, retrieved, matched_by = (
            _relevance_sets(evaluation_input)
        )

        if not expected:
            return EvaluationMetricResult(
                metric_name=self.metric_name,
                score=None,
                passed=None,
                reason=(
                    "No retrieval ground truth was configured "
                    "for this test case."
                ),
                evaluator_type=self.evaluator_type,
                evaluator_engine=self.evaluator_engine,
            )

        top_k = int(
            evaluation_input.metadata.get(
                "top_k",
                len(retrieved),
            )
            or len(retrieved)
            or 1
        )
        retrieved_at_k = retrieved[:top_k]
        relevant_count = _matched_relevant_count(
            expected,
            retrieved_at_k,
        )
        score = relevant_count / float(
            len(expected)
        )

        return EvaluationMetricResult(
            metric_name=self.metric_name,
            score=score,
            passed=None,
            reason=(
                f"{relevant_count} of {len(expected)} expected "
                f"relevant source(s) were found in the top {top_k}."
            ),
            evaluator_type=self.evaluator_type,
            evaluator_engine=self.evaluator_engine,
            metadata={
                "top_k": top_k,
                "relevant_retrieved_count": relevant_count,
                "expected_relevant_count": len(expected),
                "matched_by": matched_by,
            },
        )
