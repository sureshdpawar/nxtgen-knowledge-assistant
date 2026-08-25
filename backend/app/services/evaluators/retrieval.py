from urllib.parse import urlparse, urlunparse

from app.services.evaluators.base import (
    BaseEvaluator,
    EvaluationInput,
    EvaluationMetricResult,
)


def _normalize_url(
    value: str,
) -> str:
    """
    Normalize URLs for evaluation matching.

    Handles differences such as:

    https://nxtgeninnovate.com/
    https://nxtgeninnovate.com
    https://nxtgeninnovate.com/index.html

    It intentionally does not perform
    redirects or network calls.
    """

    value = (
        value
        .strip()
    )

    if not value:
        return ""

    try:
        parsed = urlparse(
            value
        )

    except Exception:
        return value.lower()

    scheme = (
        parsed.scheme
        .lower()
    )

    hostname = (
        parsed.hostname
        .lower()
        if parsed.hostname
        else ""
    )

    #
    # Treat www and non-www as the
    # same source identity.
    #
    if hostname.startswith(
        "www."
    ):
        hostname = (
            hostname[4:]
        )

    port = (
        parsed.port
    )

    if (
        port is not None
        and not (
            scheme == "http"
            and port == 80
        )
        and not (
            scheme == "https"
            and port == 443
        )
    ):
        netloc = (
            f"{hostname}:{port}"
        )
    else:
        netloc = hostname

    path = (
        parsed.path
        or "/"
    )

    #
    # Normalize trailing slash.
    #
    if (
        path != "/"
        and path.endswith("/")
    ):
        path = (
            path.rstrip("/")
        )

    #
    # Website crawlers commonly store
    # either "/" or "/index.html".
    #
    if path == "/index.html":
        path = "/"

    normalized = urlunparse(
        (
            scheme,
            netloc,
            path,
            "",
            parsed.query,
            "",
        )
    )

    return normalized.lower()


def _normalize_external_id(
    value: str,
) -> str:
    """
    Normalize provider-neutral external IDs.

    URLs receive URL normalization.

    Other external IDs are compared as
    trimmed lowercase strings.
    """

    value = (
        value
        .strip()
    )

    if (
        value.startswith(
            "http://"
        )
        or value.startswith(
            "https://"
        )
    ):
        return _normalize_url(
            value
        )

    return value.lower()


class HitAtKEvaluator(
    BaseEvaluator
):
    """
    Determine whether expected retrieval
    ground truth appears within top K.

    Ground-truth priority:

    1. expected_chunk_id
    2. expected_document_id
    3. expected_sources

    Portable expected_sources can use:

    {
        "type": "url",
        "value": "https://..."
    }

    or:

    {
        "type": "external_id",
        "value": "..."
    }
    """

    metric_name = (
        "hit_at_k"
    )

    evaluator_type = (
        "deterministic"
    )

    evaluator_engine = (
        "knowgentiq"
    )

    def evaluate(
        self,
        evaluation_input:
            EvaluationInput,
    ) -> EvaluationMetricResult:
        metadata = (
            evaluation_input
            .metadata
        )

        expected_document_id = (
            metadata.get(
                "expected_document_id"
            )
        )

        expected_chunk_id = (
            metadata.get(
                "expected_chunk_id"
            )
        )

        expected_sources = (
            metadata.get(
                "expected_sources",
                [],
            )
            or []
        )

        retrieved_document_ids = (
            metadata.get(
                "retrieved_document_ids",
                [],
            )
            or []
        )

        retrieved_chunk_ids = (
            metadata.get(
                "retrieved_chunk_ids",
                [],
            )
            or []
        )

        retrieved_external_ids = (
            metadata.get(
                "retrieved_document_external_ids",
                [],
            )
            or []
        )

        expected_rank = None

        matched_by = None

        matched_expected_source = None

        matched_retrieved_source = None

        #
        # 1. Chunk-level ground truth.
        #
        if expected_chunk_id is not None:
            expected_chunk_id = str(
                expected_chunk_id
            )

            for (
                index,
                chunk_id,
            ) in enumerate(
                retrieved_chunk_ids,
                start=1,
            ):
                if (
                    str(
                        chunk_id
                    )
                    == expected_chunk_id
                ):
                    expected_rank = (
                        index
                    )

                    matched_by = (
                        "chunk_id"
                    )

                    break

        #
        # 2. Document-level ground truth.
        #
        elif (
            expected_document_id
            is not None
        ):
            expected_document_id = str(
                expected_document_id
            )

            for (
                index,
                document_id,
            ) in enumerate(
                retrieved_document_ids,
                start=1,
            ):
                if (
                    str(
                        document_id
                    )
                    == expected_document_id
                ):
                    expected_rank = (
                        index
                    )

                    matched_by = (
                        "document_id"
                    )

                    break

        #
        # 3. Portable external source
        # ground truth.
        #
        elif expected_sources:
            normalized_expected = []

            for source in (
                expected_sources
            ):
                if not isinstance(
                    source,
                    dict,
                ):
                    continue

                source_type = (
                    str(
                        source.get(
                            "type",
                            "",
                        )
                    )
                    .strip()
                    .lower()
                )

                source_value = (
                    str(
                        source.get(
                            "value",
                            "",
                        )
                    )
                    .strip()
                )

                if not source_value:
                    continue

                if source_type == "url":
                    normalized_value = (
                        _normalize_url(
                            source_value
                        )
                    )

                elif (
                    source_type
                    == "external_id"
                ):
                    normalized_value = (
                        _normalize_external_id(
                            source_value
                        )
                    )

                else:
                    continue

                normalized_expected.append(
                    {
                        "type":
                            source_type,

                        "original":
                            source_value,

                        "normalized":
                            normalized_value,
                    }
                )

            for (
                index,
                retrieved_value,
            ) in enumerate(
                retrieved_external_ids,
                start=1,
            ):
                if not retrieved_value:
                    continue

                normalized_retrieved = (
                    _normalize_external_id(
                        str(
                            retrieved_value
                        )
                    )
                )

                for expected in (
                    normalized_expected
                ):
                    if (
                        normalized_retrieved
                        == expected[
                            "normalized"
                        ]
                    ):
                        expected_rank = (
                            index
                        )

                        matched_by = (
                            "expected_source"
                        )

                        matched_expected_source = (
                            expected[
                                "original"
                            ]
                        )

                        matched_retrieved_source = (
                            str(
                                retrieved_value
                            )
                        )

                        break

                if (
                    expected_rank
                    is not None
                ):
                    break

        #
        # No retrieval ground truth.
        #
        else:
            return (
                EvaluationMetricResult(
                    metric_name=
                        self.metric_name,

                    score=
                        None,

                    passed=
                        None,

                    reason=(
                        "No expected document, "
                        "chunk, or portable "
                        "source was configured "
                        "for this test case."
                    ),

                    evaluator_type=
                        self.evaluator_type,

                    evaluator_engine=
                        self.evaluator_engine,

                    metadata={
                        "expected_rank":
                            None,

                        "matched_by":
                            None,
                    },
                )
            )

        hit = (
            expected_rank
            is not None
        )

        if hit:
            reason = (
                "Expected source was "
                "retrieved at rank "
                f"{expected_rank}."
            )
        else:
            reason = (
                "Expected source was not "
                "found in the retrieved "
                "top-K results."
            )

        return (
            EvaluationMetricResult(
                metric_name=
                    self.metric_name,

                score=
                    (
                        1.0
                        if hit
                        else 0.0
                    ),

                passed=
                    hit,

                threshold=
                    1.0,

                reason=
                    reason,

                evaluator_type=
                    self.evaluator_type,

                evaluator_engine=
                    self.evaluator_engine,

                metadata={
                    "expected_rank":
                        expected_rank,

                    "matched_by":
                        matched_by,

                    "matched_expected_source":
                        matched_expected_source,

                    "matched_retrieved_source":
                        matched_retrieved_source,
                },
            )
        )


class ReciprocalRankEvaluator(
    BaseEvaluator
):
    """
    Calculate reciprocal rank.

    rank 1 -> 1.0
    rank 2 -> 0.5
    rank 3 -> 0.333...

    If retrieval ground truth exists but
    was not found, score is 0.0.

    If no retrieval ground truth exists,
    score is None so the case is excluded
    from MRR aggregation.
    """

    metric_name = (
        "reciprocal_rank"
    )

    evaluator_type = (
        "deterministic"
    )

    evaluator_engine = (
        "knowgentiq"
    )

    def evaluate(
        self,
        evaluation_input:
            EvaluationInput,
    ) -> EvaluationMetricResult:
        expected_rank = (
            evaluation_input
            .metadata
            .get(
                "expected_rank"
            )
        )

        retrieval_ground_truth = (
            evaluation_input
            .metadata
            .get(
                "has_retrieval_ground_truth",
                False,
            )
        )

        if not retrieval_ground_truth:
            return (
                EvaluationMetricResult(
                    metric_name=
                        self.metric_name,

                    score=
                        None,

                    passed=
                        None,

                    reason=(
                        "No retrieval ground "
                        "truth was configured "
                        "for this test case."
                    ),

                    evaluator_type=
                        self.evaluator_type,

                    evaluator_engine=
                        self.evaluator_engine,
                )
            )

        if expected_rank is None:
            return (
                EvaluationMetricResult(
                    metric_name=
                        self.metric_name,

                    score=
                        0.0,

                    passed=
                        False,

                    reason=(
                        "Expected source was "
                        "not found in the "
                        "retrieved results."
                    ),

                    evaluator_type=
                        self.evaluator_type,

                    evaluator_engine=
                        self.evaluator_engine,
                )
            )

        reciprocal_rank = (
            1.0
            / float(
                expected_rank
            )
        )

        return (
            EvaluationMetricResult(
                metric_name=
                    self.metric_name,

                score=
                    reciprocal_rank,

                passed=
                    True,

                reason=(
                    "Reciprocal rank "
                    "calculated from "
                    "expected source rank "
                    f"{expected_rank}."
                ),

                evaluator_type=
                    self.evaluator_type,

                evaluator_engine=
                    self.evaluator_engine,

                metadata={
                    "expected_rank":
                        expected_rank,
                },
            )
        )