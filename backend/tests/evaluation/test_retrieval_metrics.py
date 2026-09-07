import pytest

from app.services.evaluators import (
    EvaluationInput,
    EvaluatorRegistry,
)


def make_input(
    *,
    expected_sources,
    retrieved_sources,
    top_k,
    expected_rank=None,
):
    metadata = {
        "top_k": top_k,
        "expected_document_id": None,
        "expected_chunk_id": None,
        "expected_sources": [
            {
                "type": "external_id",
                "value": value,
            }
            for value in expected_sources
        ],
        "retrieved_document_ids": [],
        "retrieved_document_external_ids":
            list(retrieved_sources),
        "retrieved_chunk_ids": [],
    }

    if expected_rank is not None:
        metadata["expected_rank"] = (
            expected_rank
        )

    return EvaluationInput(
        question="test question",
        retrieved_context=[],
        expected_context=[],
        metadata=metadata,
    )


def evaluate_all(
    *,
    expected_sources,
    retrieved_sources,
    top_k,
):
    registry = EvaluatorRegistry()

    #
    # Hit@K
    #
    hit_input = make_input(
        expected_sources=expected_sources,
        retrieved_sources=retrieved_sources,
        top_k=top_k,
    )

    hit = registry.get(
        "hit_at_k"
    ).evaluate(
        hit_input
    )

    expected_rank = (
        hit.metadata.get(
            "expected_rank"
        )
    )

    #
    # Precision@K
    #
    precision_input = make_input(
        expected_sources=expected_sources,
        retrieved_sources=retrieved_sources,
        top_k=top_k,
    )

    precision = registry.get(
        "precision_at_k"
    ).evaluate(
        precision_input
    )

    #
    # Recall@K
    #
    recall_input = make_input(
        expected_sources=expected_sources,
        retrieved_sources=retrieved_sources,
        top_k=top_k,
    )

    recall = registry.get(
        "recall_at_k"
    ).evaluate(
        recall_input
    )

    #
    # Reciprocal Rank
    #
    rr_input = make_input(
        expected_sources=expected_sources,
        retrieved_sources=retrieved_sources,
        top_k=top_k,
        expected_rank=expected_rank,
    )

    rr = registry.get(
        "reciprocal_rank"
    ).evaluate(
        rr_input
    )

    return (
        hit,
        precision,
        recall,
        rr,
    )


def test_relevant_source_at_rank_one():
    (
        hit,
        precision,
        recall,
        rr,
    ) = evaluate_all(
        expected_sources=["A"],
        retrieved_sources=[
            "A",
            "X",
            "Y",
        ],
        top_k=3,
    )

    assert hit.score == 1.0
    assert hit.passed is True

    assert precision.score == pytest.approx(
        1 / 3
    )

    assert recall.score == 1.0

    assert rr.score == 1.0


def test_relevant_source_at_rank_three():
    (
        hit,
        precision,
        recall,
        rr,
    ) = evaluate_all(
        expected_sources=["A"],
        retrieved_sources=[
            "X",
            "Y",
            "A",
        ],
        top_k=3,
    )

    assert hit.score == 1.0
    assert hit.passed is True

    assert precision.score == pytest.approx(
        1 / 3
    )

    assert recall.score == 1.0

    assert rr.score == pytest.approx(
        1 / 3
    )


def test_relevant_source_not_retrieved():
    (
        hit,
        precision,
        recall,
        rr,
    ) = evaluate_all(
        expected_sources=["A"],
        retrieved_sources=[
            "X",
            "Y",
            "Z",
        ],
        top_k=3,
    )

    assert hit.score == 0.0
    assert hit.passed is False

    assert precision.score == 0.0

    assert recall.score == 0.0

    assert rr.score == 0.0


def test_partial_multi_source_retrieval():
    (
        hit,
        precision,
        recall,
        rr,
    ) = evaluate_all(
        expected_sources=[
            "A",
            "B",
            "C",
        ],
        retrieved_sources=[
            "X",
            "A",
            "Y",
        ],
        top_k=3,
    )

    assert hit.score == 1.0

    assert precision.score == pytest.approx(
        1 / 3
    )

    assert recall.score == pytest.approx(
        1 / 3
    )

    assert rr.score == pytest.approx(
        1 / 2
    )


def test_all_expected_sources_retrieved():
    (
        hit,
        precision,
        recall,
        rr,
    ) = evaluate_all(
        expected_sources=[
            "A",
            "B",
        ],
        retrieved_sources=[
            "A",
            "X",
            "B",
        ],
        top_k=3,
    )

    assert hit.score == 1.0

    assert precision.score == pytest.approx(
        2 / 3
    )

    assert recall.score == 1.0

    assert rr.score == 1.0


def test_duplicate_relevant_source_counts_once():
    (
        hit,
        precision,
        recall,
        rr,
    ) = evaluate_all(
        expected_sources=[
            "A",
            "B",
        ],
        retrieved_sources=[
            "A",
            "A",
            "A",
        ],
        top_k=3,
    )

    assert hit.score == 1.0

    assert precision.score == pytest.approx(
        1 / 3
    )

    assert recall.score == pytest.approx(
        1 / 2
    )

    assert rr.score == 1.0


def test_two_relevant_sources_in_top_five():
    (
        hit,
        precision,
        recall,
        rr,
    ) = evaluate_all(
        expected_sources=[
            "A",
            "B",
            "C",
        ],
        retrieved_sources=[
            "X",
            "B",
            "Y",
            "C",
            "Z",
        ],
        top_k=5,
    )

    assert hit.score == 1.0

    assert precision.score == pytest.approx(
        2 / 5
    )

    assert recall.score == pytest.approx(
        2 / 3
    )

    assert rr.score == pytest.approx(
        1 / 2
    )