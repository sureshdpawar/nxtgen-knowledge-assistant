from types import SimpleNamespace
from uuid import uuid4

from app.services.document_search_service import (
    DocumentSearchService,
)


def test_search_uses_expanded_candidate_top_k_when_no_override():
    service = DocumentSearchService()

    knowledge_base_id = uuid4()

    knowledge_base = SimpleNamespace(
        effective_top_k=5,
    )

    db = SimpleNamespace()

    db.get = lambda model, object_id: (
        knowledge_base
    )

    service.embedding_service.embed = (
        lambda query: [0.1, 0.2, 0.3]
    )

    captured = {}

    def fake_search(
        db,
        knowledge_base_id,
        query_embedding,
        top_k,
    ):
        captured["top_k"] = top_k

        return []

    service.embedding_repository.search = (
        fake_search
    )

    service.search(
        db=db,
        knowledge_base_id=knowledge_base_id,
        query="test question",
    )

    assert captured["top_k"] == 15


def test_search_uses_expanded_top_k_override():
    service = DocumentSearchService()

    knowledge_base_id = uuid4()

    knowledge_base = SimpleNamespace(
        effective_top_k=5,
    )

    db = SimpleNamespace()

    db.get = lambda model, object_id: (
        knowledge_base
    )

    service.embedding_service.embed = (
        lambda query: [0.1, 0.2, 0.3]
    )

    captured = {}

    def fake_search(
        db,
        knowledge_base_id,
        query_embedding,
        top_k,
    ):
        captured["top_k"] = top_k

        return []

    service.embedding_repository.search = (
        fake_search
    )

    service.search(
        db=db,
        knowledge_base_id=knowledge_base_id,
        query="test question",
        top_k_override=8,
    )

    assert captured["top_k"] == 24


def test_candidate_top_k_expands_final_context():
    assert (
        DocumentSearchService
        ._candidate_top_k(5)
        == 15
    )


def test_candidate_top_k_expands_override():
    assert (
        DocumentSearchService
        ._candidate_top_k(8)
        == 24
    )


def test_candidate_top_k_has_upper_bound():
    assert (
        DocumentSearchService
        ._candidate_top_k(100)
        == 50
    )
    
def test_search_reranks_candidates_to_final_top_k():
    service = DocumentSearchService()

    knowledge_base_id = uuid4()

    knowledge_base = SimpleNamespace(
        effective_top_k=5,
    )

    db = SimpleNamespace()

    db.get = lambda model, object_id: (
        knowledge_base
    )

    service.embedding_service.embed = (
        lambda query: [0.1, 0.2, 0.3]
    )

    candidates = [
        object()
        for _ in range(15)
    ]

    service.embedding_repository.search = (
        lambda **kwargs: candidates
    )

    captured = {}

    def fake_rerank(
        query,
        candidates,
        top_k,
    ):
        captured["query"] = query
        captured["candidate_count"] = (
            len(candidates)
        )
        captured["top_k"] = top_k

        return candidates[:top_k]

    service.reranker_service.rerank = (
        fake_rerank
    )

    results = service.search(
        db=db,
        knowledge_base_id=knowledge_base_id,
        query="test question",
    )

    assert captured["query"] == (
        "test question"
    )

    assert (
        captured["candidate_count"]
        == 15
    )

    assert captured["top_k"] == 5

    assert len(results) == 5