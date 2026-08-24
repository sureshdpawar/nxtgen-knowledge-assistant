from types import SimpleNamespace
from uuid import uuid4

from app.services.document_search_service import (
    DocumentSearchService,
)


def test_search_uses_effective_top_k_when_no_override():
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

    assert captured["top_k"] == 5


def test_search_uses_top_k_override():
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

    assert captured["top_k"] == 8