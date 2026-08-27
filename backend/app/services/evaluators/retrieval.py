from urllib.parse import (
    urlsplit,
    urlunsplit,
)

from app.services.evaluators.base import (
    BaseEvaluator,
    EvaluationInput,
    EvaluationMetricResult,
)


def _normalize_url(
    value: str,
) -> str:
    """
    Normalize URLs used as retrieval
    ground truth.

    Examples:

    https://example.com/
    https://example.com
        -> same value

    Query strings and fragments are removed
    because enterprise source identity should
    normally represent the underlying page.
    """

    value = (
        value
        .strip()
    )

    if not value:
        return ""

    try:
        parts = urlsplit(
            value
        )

        scheme = (
            parts.scheme
            .lower()
        )

        netloc = (
            parts.netloc
            .lower()
        )

        path = (
            parts.path
            or "/"
        )

        #
        # Treat trailing slash as equivalent.
        #
        if (
            path != "/"
            and path.endswith("/")
        ):
            path = (
                path.rstrip("/")
            )

        #
        # Treat root "/" as empty.
        #
        if path == "/":
            path = ""

        return urlunsplit(
            (
                scheme,
                netloc,
                path,
                "",
                "",
            )
        )

    except Exception:
        return (
            value
            .rstrip("/")
            .lower()
        )


def _normalize_external_id(
    value: str,
) -> str:
    """
    Normalize document external IDs.

    Website-ingested documents currently
    commonly use their source URL as the
    document external_id.
    """

    value = (
        value
        .strip()
    )

    if not value:
        return ""

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


def _normalize_expected_sources(
    expected_sources: list,
) -> set[str]:
    """
    Convert configured expected sources
    into normalized identities.

    Supported source types in V1:

    - url
    - external_id
    """

    normalized_sources: set[
        str
    ] = set()

    for source in (
        expected_sources
        or []
    ):
        if not isinstance(
            source,
            dict,
        ):
            continue

        source_type = str(
            source.get(
                "type",
                "",
            )
        ).strip().lower()

        source_value = str(
            source.get(
                "value",
                "",
            )
        ).strip()

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
            #
            # Unknown source types are not
            # considered retrieval ground
            # truth by this evaluator.
            #
            continue

        if normalized_value:
            normalized_sources.add(
                normalized_value
            )

    return normalized_sources


def _resolve_relevance_data(
    evaluation_input:
        EvaluationInput,
) -> tuple[
    set[str],
    list[str],
    str | None,
]:
    """
    Resolve expected relevant identities
    and retrieved identities using the most
    specific configured ground truth.

    Priority:

    1. expected_chunk_id
    2. expected_document_id
    3. expected_sources

    This keeps the behavior compatible with
    existing golden datasets while allowing
    source-based datasets to support multiple
    relevant sources.
    """

    metadata = (
        evaluation_input.metadata
    )

    expected_chunk_id = (
        metadata.get(
            "expected_chunk_id"
        )
    )

    if (
        expected_chunk_id
        is not None
    ):
        expected = {
            str(
                expected_chunk_id
            )
        }

        retrieved = [
            str(
                value
            )
            for value in (
                metadata.get(
                    "retrieved_chunk_ids",
                    [],
                )
                or []
            )
            if value is not None
        ]

        return (
            expected,
            retrieved,
            "chunk_id",
        )

    expected_document_id = (
        metadata.get(
            "expected_document_id"
        )
    )

    if (
        expected_document_id
        is not None
    ):
        expected = {
            str(
                expected_document_id
            )
        }

        retrieved = [
            str(
                value
            )
            for value in (
                metadata.get(
                    "retrieved_document_ids",
                    [],
                )
                or []
            )
            if value is not None
        ]

        return (
            expected,
            retrieved,
            "document_id",
        )

    expected_sources = (
        _normalize_expected_sources(
            metadata.get(
                "expected_sources",
                [],
            )
            or []
        )
    )

    if expected_sources:
        retrieved = [
            _normalize_external_id(
                str(
                    value
                )
            )
            for value in (
                metadata.get(
                    "retrieved_document_external_ids",
                    [],
                )
                or []
            )
            if value
        ]

        return (
            expected_sources,
            retrieved,
            "expected_source",
        )

    return (
        set(),
        [],
        None,
    )


def _first_relevant_rank(
    expected: set[str],
    retrieved: list[str],
    top_k: int,
) -> int | None:
    """
    Return the 1-based rank of the first
    relevant retrieved identity.
    """

    for (
        index,
        retrieved_value,
    ) in enumerate(
        retrieved[
            :top_k
        ],
        start=1,
    ):
        if (
            retrieved_value
            in expected
        ):
            return index

    return None


def _unique_relevant_retrieved(
    expected: set[str],
    retrieved: list[str],
    top_k: int,
) -> set[str]:
    """
    Return unique relevant identities found
    in the first K retrieval results.

    Multiple chunks from the same relevant
    document/source must not artificially
    increase the number of relevant sources.
    """

    return (
        expected.intersection(
            set(
                retrieved[
                    :top_k
                ]
            )
        )
    )


class HitAtKEvaluator(
    BaseEvaluator
):
    """
    Determine whether at least one expected
    relevant item appears in the first K
    retrieval results.
    """

    metric_name = "hit_at_k"

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
        (
            expected,
            retrieved,
            matched_by,
        ) = _resolve_relevance_data(
            evaluation_input
        )

        if not expected:
            return (
                EvaluationMetricResult(
                    metric_name=
                        self.metric_name,

                    score=None,

                    passed=None,

                    reason=(
                        "No retrieval "
                        "ground truth was "
                        "configured for "
                        "this test case."
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

        top_k = int(
            evaluation_input
            .metadata
            .get(
                "top_k",
                len(
                    retrieved
                ),
            )
            or len(
                retrieved
            )
            or 1
        )

        expected_rank = (
            _first_relevant_rank(
                expected=
                    expected,

                retrieved=
                    retrieved,

                top_k=
                    top_k,
            )
        )

        hit = (
            expected_rank
            is not None
        )

        return (
            EvaluationMetricResult(
                metric_name=
                    self.metric_name,

                score=(
                    1.0
                    if hit
                    else 0.0
                ),

                passed=
                    hit,

                reason=(
                    (
                        "Relevant retrieval "
                        "ground truth was "
                        "found at rank "
                        f"{expected_rank}."
                    )
                    if hit
                    else
                    (
                        "No relevant "
                        "retrieval ground "
                        "truth was found "
                        f"in the top {top_k}."
                    )
                ),

                evaluator_type=
                    self.evaluator_type,

                evaluator_engine=
                    self.evaluator_engine,

                metadata={
                    "top_k":
                        top_k,

                    "expected_rank":
                        expected_rank,

                    "matched_by":
                        matched_by,

                    "expected_relevant_count":
                        len(
                            expected
                        ),
                },
            )
        )


class PrecisionAtKEvaluator(
    BaseEvaluator
):
    """
    Precision@K.

    Of the K requested retrieval positions,
    what fraction contains a unique relevant
    source?

    Example:

    Expected:
        A, B

    Retrieved Top 3:
        A, X, B

    Precision@3:
        2 / 3 = 0.667

    For source/document-level relevance,
    duplicate chunks from the same document
    are counted once as a relevant identity.
    """

    metric_name = (
        "precision_at_k"
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
        (
            expected,
            retrieved,
            matched_by,
        ) = _resolve_relevance_data(
            evaluation_input
        )

        if not expected:
            return (
                EvaluationMetricResult(
                    metric_name=
                        self.metric_name,

                    score=None,

                    passed=None,

                    reason=(
                        "No retrieval "
                        "ground truth was "
                        "configured for "
                        "this test case."
                    ),

                    evaluator_type=
                        self.evaluator_type,

                    evaluator_engine=
                        self.evaluator_engine,
                )
            )

        top_k = int(
            evaluation_input
            .metadata
            .get(
                "top_k",
                len(
                    retrieved
                ),
            )
            or len(
                retrieved
            )
            or 1
        )

        relevant_retrieved = (
            _unique_relevant_retrieved(
                expected=
                    expected,

                retrieved=
                    retrieved,

                top_k=
                    top_k,
            )
        )

        relevant_count = len(
            relevant_retrieved
        )

        #
        # Standard Precision@K denominator
        # is K, not number of returned rows.
        #
        precision = (
            relevant_count
            / float(
                top_k
            )
        )

        return (
            EvaluationMetricResult(
                metric_name=
                    self.metric_name,

                score=
                    precision,

                passed=None,

                reason=(
                    f"{relevant_count} "
                    "unique relevant "
                    "source(s) were found "
                    f"in the top {top_k}."
                ),

                evaluator_type=
                    self.evaluator_type,

                evaluator_engine=
                    self.evaluator_engine,

                metadata={
                    "top_k":
                        top_k,

                    "relevant_retrieved_count":
                        relevant_count,

                    "expected_relevant_count":
                        len(
                            expected
                        ),

                    "matched_by":
                        matched_by,
                },
            )
        )


class RecallAtKEvaluator(
    BaseEvaluator
):
    """
    Recall@K.

    Of all expected relevant sources, what
    fraction were retrieved in the first K?

    Example:

    Expected:
        A, B

    Retrieved Top 3:
        A, X, B

    Recall@3:
        2 / 2 = 1.0
    """

    metric_name = (
        "recall_at_k"
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
        (
            expected,
            retrieved,
            matched_by,
        ) = _resolve_relevance_data(
            evaluation_input
        )

        if not expected:
            return (
                EvaluationMetricResult(
                    metric_name=
                        self.metric_name,

                    score=None,

                    passed=None,

                    reason=(
                        "No retrieval "
                        "ground truth was "
                        "configured for "
                        "this test case."
                    ),

                    evaluator_type=
                        self.evaluator_type,

                    evaluator_engine=
                        self.evaluator_engine,
                )
            )

        top_k = int(
            evaluation_input
            .metadata
            .get(
                "top_k",
                len(
                    retrieved
                ),
            )
            or len(
                retrieved
            )
            or 1
        )

        relevant_retrieved = (
            _unique_relevant_retrieved(
                expected=
                    expected,

                retrieved=
                    retrieved,

                top_k=
                    top_k,
            )
        )

        relevant_count = len(
            relevant_retrieved
        )

        recall = (
            relevant_count
            / float(
                len(
                    expected
                )
            )
        )

        return (
            EvaluationMetricResult(
                metric_name=
                    self.metric_name,

                score=
                    recall,

                passed=None,

                reason=(
                    f"{relevant_count} "
                    f"of {len(expected)} "
                    "expected relevant "
                    "source(s) were found "
                    f"in the top {top_k}."
                ),

                evaluator_type=
                    self.evaluator_type,

                evaluator_engine=
                    self.evaluator_engine,

                metadata={
                    "top_k":
                        top_k,

                    "relevant_retrieved_count":
                        relevant_count,

                    "expected_relevant_count":
                        len(
                            expected
                        ),

                    "matched_by":
                        matched_by,
                },
            )
        )


class ReciprocalRankEvaluator(
    BaseEvaluator
):
    """
    Reciprocal Rank.

    Measures how early the first relevant
    retrieval result appears.

    Rank 1 -> 1.0
    Rank 2 -> 0.5
    Rank 3 -> 0.333...
    No hit -> 0.0

    MRR is calculated by averaging this
    value across scored evaluation cases.
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
        (
            expected,
            retrieved,
            matched_by,
        ) = _resolve_relevance_data(
            evaluation_input
        )

        if not expected:
            return (
                EvaluationMetricResult(
                    metric_name=
                        self.metric_name,

                    score=None,

                    passed=None,

                    reason=(
                        "No retrieval "
                        "ground truth was "
                        "configured for "
                        "this test case."
                    ),

                    evaluator_type=
                        self.evaluator_type,

                    evaluator_engine=
                        self.evaluator_engine,
                )
            )

        top_k = int(
            evaluation_input
            .metadata
            .get(
                "top_k",
                len(
                    retrieved
                ),
            )
            or len(
                retrieved
            )
            or 1
        )

        expected_rank = (
            evaluation_input
            .metadata
            .get(
                "expected_rank"
            )
        )

        #
        # Allow this evaluator to operate
        # independently from Hit@K too.
        #
        if expected_rank is None:
            expected_rank = (
                _first_relevant_rank(
                    expected=
                        expected,

                    retrieved=
                        retrieved,

                    top_k=
                        top_k,
                )
            )

        reciprocal_rank = (
            (
                1.0
                / float(
                    expected_rank
                )
            )
            if expected_rank
            else 0.0
        )

        return (
            EvaluationMetricResult(
                metric_name=
                    self.metric_name,

                score=
                    reciprocal_rank,

                passed=(
                    expected_rank
                    is not None
                ),

                reason=(
                    (
                        "First relevant "
                        "result was found "
                        "at rank "
                        f"{expected_rank}."
                    )
                    if expected_rank
                    else
                    (
                        "No relevant result "
                        f"was found in the "
                        f"top {top_k}."
                    )
                ),

                evaluator_type=
                    self.evaluator_type,

                evaluator_engine=
                    self.evaluator_engine,

                metadata={
                    "top_k":
                        top_k,

                    "expected_rank":
                        expected_rank,

                    "matched_by":
                        matched_by,
                },
            )
        )
        
class PrecisionAtKEvaluator(
    BaseEvaluator
):
    """
    Calculate Precision@K.

    Precision@K answers:

        Of the K retrieved results,
        what fraction are relevant?

    For the current Knowgentiq golden
    dataset model, relevance is determined
    using the configured retrieval ground
    truth:

    - expected_chunk_id
    - expected_document_id
    - expected_sources

    When the case contains one expected
    source, at most one retrieved result
    can currently be counted as relevant.

    Example:

        top_k = 5
        expected source found at rank 2

        relevant retrieved = 1
        retrieved count = 5

        Precision@5 = 1 / 5 = 0.20

    If fewer than K results are returned,
    the denominator is the number of
    retrieved results rather than K.

    Cases without retrieval ground truth
    are unscored.
    """

    metric_name = (
        "precision_at_k"
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

        has_retrieval_ground_truth = (
            metadata.get(
                "has_retrieval_ground_truth",
                False,
            )
        )

        if not has_retrieval_ground_truth:
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

        expected_rank = (
            metadata.get(
                "expected_rank"
            )
        )

        top_k = int(
            metadata.get(
                "top_k",
                0,
            )
            or 0
        )

        retrieved_chunk_ids = (
            metadata.get(
                "retrieved_chunk_ids",
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

        retrieved_external_ids = (
            metadata.get(
                "retrieved_document_external_ids",
                [],
            )
            or []
        )

        retrieved_count = max(
            len(
                retrieved_chunk_ids
            ),
            len(
                retrieved_document_ids
            ),
            len(
                retrieved_external_ids
            ),
        )

        if top_k > 0:
            retrieved_count = min(
                retrieved_count,
                top_k,
            )

        if retrieved_count == 0:
            return (
                EvaluationMetricResult(
                    metric_name=
                        self.metric_name,

                    score=
                        0.0,

                    passed=
                        False,

                    threshold=
                        0.0,

                    reason=(
                        "No results were "
                        "retrieved."
                    ),

                    evaluator_type=
                        self.evaluator_type,

                    evaluator_engine=
                        self.evaluator_engine,

                    metadata={
                        "relevant_retrieved_count":
                            0,

                        "retrieved_count":
                            0,

                        "top_k":
                            top_k,
                    },
                )
            )

        relevant_retrieved_count = (
            1
            if expected_rank is not None
            else 0
        )

        precision_at_k = (
            relevant_retrieved_count
            / retrieved_count
        )

        return (
            EvaluationMetricResult(
                metric_name=
                    self.metric_name,

                score=
                    precision_at_k,

                passed=
                    (
                        relevant_retrieved_count
                        > 0
                    ),

                threshold=
                    0.0,

                reason=(
                    "Precision@K calculated "
                    "from relevant retrieved "
                    "results divided by total "
                    "retrieved results."
                ),

                evaluator_type=
                    self.evaluator_type,

                evaluator_engine=
                    self.evaluator_engine,

                metadata={
                    "relevant_retrieved_count":
                        relevant_retrieved_count,

                    "retrieved_count":
                        retrieved_count,

                    "top_k":
                        top_k,

                    "expected_rank":
                        expected_rank,
                },
            )
        )


class RecallAtKEvaluator(
    BaseEvaluator
):
    """
    Calculate Recall@K.

    Recall@K answers:

        Of all expected relevant sources,
        what fraction were retrieved?

    The current Knowgentiq golden case
    model supports:

    - one expected_chunk_id
    - one expected_document_id
    - multiple expected_sources

    expected_chunk_id and
    expected_document_id represent one
    relevant target.

    expected_sources can represent multiple
    acceptable relevant sources.

    Cases without retrieval ground truth
    are unscored.
    """

    metric_name = (
        "recall_at_k"
    )

    evaluator_type = (
        "deterministic"
    )

    evaluator_engine = (
        "knowgentiq"
    )

    def _normalize_expected_sources(
        self,
        expected_sources: list,
    ) -> set[str]:
        normalized = set()

        for source in expected_sources:
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

            if normalized_value:
                normalized.add(
                    normalized_value
                )

        return normalized

    def evaluate(
        self,
        evaluation_input:
            EvaluationInput,
    ) -> EvaluationMetricResult:
        metadata = (
            evaluation_input
            .metadata
        )

        has_retrieval_ground_truth = (
            metadata.get(
                "has_retrieval_ground_truth",
                False,
            )
        )

        if not has_retrieval_ground_truth:
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

        expected_chunk_id = (
            metadata.get(
                "expected_chunk_id"
            )
        )

        expected_document_id = (
            metadata.get(
                "expected_document_id"
            )
        )

        expected_sources = (
            metadata.get(
                "expected_sources",
                [],
            )
            or []
        )

        retrieved_chunk_ids = [
            str(
                value
            )
            for value
            in (
                metadata.get(
                    "retrieved_chunk_ids",
                    [],
                )
                or []
            )
            if value is not None
        ]

        retrieved_document_ids = [
            str(
                value
            )
            for value
            in (
                metadata.get(
                    "retrieved_document_ids",
                    [],
                )
                or []
            )
            if value is not None
        ]

        retrieved_external_ids = {
            _normalize_external_id(
                str(
                    value
                )
            )
            for value
            in (
                metadata.get(
                    "retrieved_document_external_ids",
                    [],
                )
                or []
            )
            if value
        }

        relevant_expected_count = 0
        relevant_retrieved_count = 0

        #
        # Follow the same ground-truth
        # priority used by Hit@K.
        #
        if expected_chunk_id is not None:
            relevant_expected_count = 1

            expected_value = str(
                expected_chunk_id
            )

            if (
                expected_value
                in retrieved_chunk_ids
            ):
                relevant_retrieved_count = 1

        elif expected_document_id is not None:
            relevant_expected_count = 1

            expected_value = str(
                expected_document_id
            )

            if (
                expected_value
                in retrieved_document_ids
            ):
                relevant_retrieved_count = 1

        elif expected_sources:
            normalized_expected = (
                self
                ._normalize_expected_sources(
                    expected_sources
                )
            )

            relevant_expected_count = len(
                normalized_expected
            )

            relevant_retrieved_count = len(
                normalized_expected
                .intersection(
                    retrieved_external_ids
                )
            )

        if relevant_expected_count == 0:
            return (
                EvaluationMetricResult(
                    metric_name=
                        self.metric_name,

                    score=
                        None,

                    passed=
                        None,

                    reason=(
                        "Retrieval ground truth "
                        "was configured but no "
                        "supported expected "
                        "sources could be "
                        "evaluated."
                    ),

                    evaluator_type=
                        self.evaluator_type,

                    evaluator_engine=
                        self.evaluator_engine,

                    metadata={
                        "relevant_expected_count":
                            0,

                        "relevant_retrieved_count":
                            0,
                    },
                )
            )

        recall_at_k = (
            relevant_retrieved_count
            / relevant_expected_count
        )

        return (
            EvaluationMetricResult(
                metric_name=
                    self.metric_name,

                score=
                    recall_at_k,

                passed=
                    (
                        relevant_retrieved_count
                        > 0
                    ),

                threshold=
                    0.0,

                reason=(
                    "Recall@K calculated from "
                    "retrieved relevant sources "
                    "divided by all expected "
                    "relevant sources."
                ),

                evaluator_type=
                    self.evaluator_type,

                evaluator_engine=
                    self.evaluator_engine,

                metadata={
                    "relevant_expected_count":
                        relevant_expected_count,

                    "relevant_retrieved_count":
                        relevant_retrieved_count,

                    "top_k":
                        metadata.get(
                            "top_k"
                        ),
                },
            )
        )