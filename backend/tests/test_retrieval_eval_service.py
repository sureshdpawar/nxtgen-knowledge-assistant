from types import SimpleNamespace
from uuid import uuid4

from app.services.retrieval_eval_service import RetrievalEvalService


def test_evaluate_case_calculates_rank_and_reciprocal_rank():
    service = RetrievalEvalService()

    expected_document_id = uuid4()
    eval_case = SimpleNamespace(
        question="What does NXTGEN do?",
        expected_document_id=expected_document_id,
    )

    rows = []
    for index in range(3):
        document_id = (
            expected_document_id
            if index == 1
            else uuid4()
        )
        rows.append(
            (
                SimpleNamespace(id=uuid4()),
                SimpleNamespace(id=document_id),
                SimpleNamespace(id=uuid4()),
                0.1 + index,
            )
        )

    service.search_service.search = lambda **kwargs: rows

    result = service.evaluate_case(
        db=SimpleNamespace(),
        knowledge_base_id=uuid4(),
        eval_case=eval_case,
        top_k=5,
    )

    assert result["expected_rank"] == 2
    assert result["hit_at_k"] is True
    assert result["reciprocal_rank"] == 0.5


def test_aggregate_calculates_hit_rate_and_mrr():
    result = RetrievalEvalService.aggregate(
        [
            {"hit_at_k": True, "reciprocal_rank": 1.0},
            {"hit_at_k": True, "reciprocal_rank": 0.5},
            {"hit_at_k": False, "reciprocal_rank": 0.0},
        ]
    )

    assert result["case_count"] == 3
    assert result["hit_rate"] == 2 / 3
    assert result["mrr"] == 0.5
