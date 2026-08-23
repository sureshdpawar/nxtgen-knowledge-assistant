from uuid import UUID

from sqlalchemy.orm import Session

from app.models.eval_case import EvalCase
from app.services.document_search_service import DocumentSearchService


class RetrievalEvalService:
    def __init__(self):
        self.search_service = DocumentSearchService()

    def evaluate_case(
        self,
        db: Session,
        knowledge_base_id: UUID,
        eval_case: EvalCase,
        top_k: int,
    ) -> dict:
        results = self.search_service.search(
            db=db,
            knowledge_base_id=knowledge_base_id,
            query=eval_case.question,
            top_k_override=top_k,
        )

        document_ids = [
            str(document.id)
            for _, document, _, _ in results
        ]
        chunk_ids = [
            str(chunk.id)
            for chunk, _, _, _ in results
        ]
        distances = [
            float(distance)
            for _, _, _, distance in results
        ]

        expected_rank = None
        expected_document_id = (
            str(eval_case.expected_document_id)
            if eval_case.expected_document_id is not None
            else None
        )

        if expected_document_id is not None:
            for rank, document_id in enumerate(
                document_ids,
                start=1,
            ):
                if document_id == expected_document_id:
                    expected_rank = rank
                    break

        hit_at_k = expected_rank is not None
        reciprocal_rank = (
            1.0 / expected_rank
            if expected_rank is not None
            else 0.0
        )

        return {
            "retrieved_document_ids": document_ids,
            "retrieved_chunk_ids": chunk_ids,
            "retrieved_distances": distances,
            "expected_rank": expected_rank,
            "hit_at_k": hit_at_k,
            "reciprocal_rank": reciprocal_rank,
        }

    @staticmethod
    def aggregate(case_results: list[dict]) -> dict:
        if not case_results:
            return {
                "case_count": 0,
                "hit_rate": 0.0,
                "mrr": 0.0,
            }

        case_count = len(case_results)
        hit_count = sum(
            1
            for result in case_results
            if result["hit_at_k"]
        )
        reciprocal_rank_sum = sum(
            result["reciprocal_rank"]
            for result in case_results
        )

        return {
            "case_count": case_count,
            "hit_rate": hit_count / case_count,
            "mrr": reciprocal_rank_sum / case_count,
        }
