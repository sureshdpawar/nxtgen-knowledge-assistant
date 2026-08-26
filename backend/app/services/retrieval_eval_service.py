from uuid import UUID

from sqlalchemy.orm import Session

from app.models.eval_case import EvalCase
from app.services.document_search_service import DocumentSearchService
from app.services.evaluators import EvaluationInput, EvaluatorRegistry


class RetrievalEvalService:

    def __init__(self):
        self.search_service = DocumentSearchService()
        self.evaluator_registry = EvaluatorRegistry()

    def evaluate_case(
        self,
        db: Session,
        knowledge_base_id: UUID,
        eval_case: EvalCase,
        top_k: int,
    ) -> dict:
        if top_k < 1:
            raise ValueError("top_k must be greater than 0.")

        results = self.search_service.search(
            db=db,
            knowledge_base_id=knowledge_base_id,
            query=eval_case.question,
            top_k_override=top_k,
        )

        retrieved_document_ids = []
        retrieved_document_external_ids = []
        retrieved_chunk_ids = []
        retrieved_distances = []
        retrieval_context = []

        for rank, result in enumerate(results, start=1):
            chunk, document, knowledge_source, distance = result
            document_id = str(document.id)
            document_external_id = document.external_id
            chunk_id = str(chunk.id)

            retrieved_document_ids.append(document_id)
            retrieved_document_external_ids.append(document_external_id)
            retrieved_chunk_ids.append(chunk_id)
            retrieved_distances.append(float(distance))
            retrieval_context.append(
                {
                    "rank": rank,
                    "document_id": document_id,
                    "document_external_id": document_external_id,
                    "chunk_id": chunk_id,
                    "document_name": document.original_filename,
                    "knowledge_source_id": str(knowledge_source.id),
                    "knowledge_source_name": knowledge_source.name,
                    "chunk_index": chunk.chunk_index,
                    "text": chunk.text or "",
                    "distance": float(distance),
                }
            )

        return self.evaluate_retrieved_case(
            eval_case=eval_case,
            top_k=top_k,
            retrieved_document_ids=retrieved_document_ids,
            retrieved_document_external_ids=(
                retrieved_document_external_ids
            ),
            retrieved_chunk_ids=retrieved_chunk_ids,
            retrieved_distances=retrieved_distances,
            retrieval_context=retrieval_context,
        )

    def evaluate_retrieved_case(
        self,
        eval_case: EvalCase,
        top_k: int,
        retrieved_document_ids: list,
        retrieved_chunk_ids: list,
        retrieved_distances: list,
        retrieval_context: list,
        retrieved_document_external_ids: list | None = None,
    ) -> dict:
        if top_k < 1:
            raise ValueError("top_k must be greater than 0.")

        if retrieved_document_external_ids is None:
            retrieved_document_external_ids = [
                item.get("document_external_id")
                for item in retrieval_context
            ]

        expected_sources = eval_case.expected_sources or []
        has_retrieval_ground_truth = any(
            [
                eval_case.expected_document_id is not None,
                eval_case.expected_chunk_id is not None,
                bool(expected_sources),
            ]
        )

        evaluation_input = EvaluationInput(
            question=eval_case.question,
            retrieved_context=[
                item.get("text", "")
                for item in retrieval_context
            ],
            expected_context=(
                [eval_case.expected_text]
                if eval_case.expected_text
                else []
            ),
            metadata={
                "top_k": top_k,
                "expected_document_id": eval_case.expected_document_id,
                "expected_chunk_id": eval_case.expected_chunk_id,
                "expected_sources": expected_sources,
                "retrieved_document_ids": retrieved_document_ids,
                "retrieved_document_external_ids": (
                    retrieved_document_external_ids
                ),
                "retrieved_chunk_ids": retrieved_chunk_ids,
                "has_retrieval_ground_truth": (
                    has_retrieval_ground_truth
                ),
            },
        )

        hit_result = self.evaluator_registry.get(
            "hit_at_k"
        ).evaluate(evaluation_input)
        expected_rank = hit_result.metadata.get("expected_rank")
        evaluation_input.metadata["expected_rank"] = expected_rank

        precision_result = self.evaluator_registry.get(
            "precision_at_k"
        ).evaluate(evaluation_input)
        recall_result = self.evaluator_registry.get(
            "recall_at_k"
        ).evaluate(evaluation_input)
        rr_result = self.evaluator_registry.get(
            "reciprocal_rank"
        ).evaluate(evaluation_input)

        metric_results = {
            "hit_at_k": hit_result,
            "precision_at_k": precision_result,
            "recall_at_k": recall_result,
            "reciprocal_rank": rr_result,
        }
        metrics = {
            name: {
                "score": result.score,
                "passed": result.passed,
                "threshold": result.threshold,
                "reason": result.reason,
                "evaluator_type": result.evaluator_type,
                "evaluator_engine": result.evaluator_engine,
                "metadata": result.metadata,
            }
            for name, result in metric_results.items()
        }

        return {
            "retrieved_document_ids": retrieved_document_ids,
            "retrieved_document_external_ids": (
                retrieved_document_external_ids
            ),
            "retrieved_chunk_ids": retrieved_chunk_ids,
            "retrieved_distances": retrieved_distances,
            "retrieval_context": retrieval_context,
            "expected_rank": expected_rank,
            "hit_at_k": hit_result.passed,
            "precision_at_k": precision_result.score,
            "recall_at_k": recall_result.score,
            "reciprocal_rank": rr_result.score,
            "has_retrieval_ground_truth": (
                has_retrieval_ground_truth
            ),
            "metrics": metrics,
        }

    def aggregate(
        self,
        results: list[dict],
    ) -> dict:
        case_count = len(results)
        scored_results = [
            result
            for result in results
            if result.get(
                "has_retrieval_ground_truth",
                False,
            )
        ]
        scored_case_count = len(scored_results)
        unscored_case_count = case_count - scored_case_count

        empty = {
            "case_count": case_count,
            "scored_case_count": scored_case_count,
            "unscored_case_count": unscored_case_count,
            "hit_count": 0,
            "miss_count": 0,
            "hit_rate": 0.0,
            "precision_at_k": 0.0,
            "recall_at_k": 0.0,
            "mrr": 0.0,
        }
        if scored_case_count == 0:
            return empty

        hit_count = sum(
            1
            for result in scored_results
            if result.get("hit_at_k") is True
        )
        miss_count = scored_case_count - hit_count

        def average(metric_name: str) -> float:
            values = [
                float(result[metric_name])
                for result in scored_results
                if result.get(metric_name) is not None
            ]
            return (
                sum(values) / len(values)
                if values
                else 0.0
            )

        return {
            "case_count": case_count,
            "scored_case_count": scored_case_count,
            "unscored_case_count": unscored_case_count,
            "hit_count": hit_count,
            "miss_count": miss_count,
            "hit_rate": hit_count / scored_case_count,
            "precision_at_k": average("precision_at_k"),
            "recall_at_k": average("recall_at_k"),
            "mrr": average("reciprocal_rank"),
        }
