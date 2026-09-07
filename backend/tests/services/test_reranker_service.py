from types import SimpleNamespace

from app.services.reranker_service import (
    RerankerService,
)


class FakeModel:

    def __init__(self, scores):
        self.scores = scores
        self.received_pairs = None

    def predict(
        self,
        pairs,
        show_progress_bar=False,
    ):
        self.received_pairs = pairs
        return self.scores


def _candidate(text: str):
    chunk = SimpleNamespace(
        text=text,
    )

    return (
        chunk,
        None,
        None,
        0.1,
    )


def test_rerank_orders_by_cross_encoder_score(
    monkeypatch,
):
    service = RerankerService()

    model = FakeModel(
        scores=[
            0.10,
            0.95,
            0.40,
        ],
    )

    monkeypatch.setattr(
        service,
        "_get_model",
        lambda: model,
    )

    candidates = [
        _candidate("broad content"),
        _candidate("highly relevant content"),
        _candidate("somewhat relevant content"),
    ]

    results = service.rerank(
        query="What AI capabilities are provided?",
        candidates=candidates,
        top_k=2,
    )

    assert len(results) == 2

    assert (
        results[0][0].text
        == "highly relevant content"
    )

    assert (
        results[1][0].text
        == "somewhat relevant content"
    )


def test_rerank_builds_query_document_pairs(
    monkeypatch,
):
    service = RerankerService()

    model = FakeModel(
        scores=[
            0.5,
            0.4,
        ],
    )

    monkeypatch.setattr(
        service,
        "_get_model",
        lambda: model,
    )

    candidates = [
        _candidate("document one"),
        _candidate("document two"),
    ]

    service.rerank(
        query="test query",
        candidates=candidates,
        top_k=2,
    )

    assert model.received_pairs == [
        (
            "test query",
            "document one",
        ),
        (
            "test query",
            "document two",
        ),
    ]


def test_rerank_returns_empty_for_no_candidates():
    service = RerankerService()

    assert (
        service.rerank(
            query="test",
            candidates=[],
            top_k=5,
        )
        == []
    )


def test_rerank_rejects_invalid_top_k():
    service = RerankerService()

    try:
        service.rerank(
            query="test",
            candidates=[
                _candidate("document"),
            ],
            top_k=0,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError."
        )


def test_single_candidate_does_not_load_model(
    monkeypatch,
):
    service = RerankerService()

    def fail():
        raise AssertionError(
            "Model should not load."
        )

    monkeypatch.setattr(
        service,
        "_get_model",
        fail,
    )

    candidate = _candidate(
        "only document",
    )

    results = service.rerank(
        query="test",
        candidates=[candidate],
        top_k=5,
    )

    assert results == [
        candidate,
    ]