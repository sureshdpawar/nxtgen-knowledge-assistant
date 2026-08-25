from uuid import UUID

from sqlalchemy.orm import Session

from app.models.eval_case import (
    EvalCase,
)
from app.services.document_search_service import (
    DocumentSearchService,
)
from app.services.evaluators import (
    EvaluationInput,
    EvaluatorRegistry,
)


class RetrievalEvalService:

    def __init__(self):
        self.search_service = (
            DocumentSearchService()
        )

        self.evaluator_registry = (
            EvaluatorRegistry()
        )

    def evaluate_case(
        self,
        db: Session,
        knowledge_base_id: UUID,
        eval_case: EvalCase,
        top_k: int,
    ) -> dict:
        """
        Execute retrieval and evaluate
        the retrieved results.
        """

        if top_k < 1:
            raise ValueError(
                "top_k must be "
                "greater than 0."
            )

        results = (
            self.search_service.search(
                db=db,

                knowledge_base_id=
                    knowledge_base_id,

                query=
                    eval_case.question,

                top_k_override=
                    top_k,
            )
        )

        retrieved_document_ids = []

        retrieved_document_external_ids = []

        retrieved_chunk_ids = []

        retrieved_distances = []

        retrieval_context = []

        for (
            rank,
            result,
        ) in enumerate(
            results,
            start=1,
        ):
            (
                chunk,
                document,
                knowledge_source,
                distance,
            ) = result

            document_id = str(
                document.id
            )

            document_external_id = (
                document.external_id
            )

            chunk_id = str(
                chunk.id
            )

            retrieved_document_ids.append(
                document_id
            )

            retrieved_document_external_ids.append(
                document_external_id
            )

            retrieved_chunk_ids.append(
                chunk_id
            )

            retrieved_distances.append(
                float(
                    distance
                )
            )

            retrieval_context.append(
                {
                    "rank":
                        rank,

                    "document_id":
                        document_id,

                    "document_external_id":
                        document_external_id,

                    "chunk_id":
                        chunk_id,

                    "document_name":
                        document.original_filename,

                    "knowledge_source_id":
                        str(
                            knowledge_source.id
                        ),

                    "knowledge_source_name":
                        knowledge_source.name,

                    "chunk_index":
                        chunk.chunk_index,

                    "text":
                        (
                            chunk.text
                            or ""
                        ),

                    "distance":
                        float(
                            distance
                        ),
                }
            )

        return (
            self.evaluate_retrieved_case(
                eval_case=
                    eval_case,

                top_k=
                    top_k,

                retrieved_document_ids=
                    retrieved_document_ids,

                retrieved_document_external_ids=
                    retrieved_document_external_ids,

                retrieved_chunk_ids=
                    retrieved_chunk_ids,

                retrieved_distances=
                    retrieved_distances,

                retrieval_context=
                    retrieval_context,
            )
        )

    def evaluate_retrieved_case(
        self,
        eval_case: EvalCase,
        top_k: int,
        retrieved_document_ids: list,
        retrieved_chunk_ids: list,
        retrieved_distances: list,
        retrieval_context: list,
        retrieved_document_external_ids:
            list | None = None,
    ) -> dict:
        """
        Score retrieval results already
        produced by another service.

        Full RAG evaluation uses this so
        retrieval metrics are calculated
        against the exact context that was
        sent to the generator.
        """

        if top_k < 1:
            raise ValueError(
                "top_k must be "
                "greater than 0."
            )

        if (
            retrieved_document_external_ids
            is None
        ):
            retrieved_document_external_ids = [
                item.get(
                    "document_external_id"
                )
                for item
                in retrieval_context
            ]

        expected_sources = (
            eval_case.expected_sources
            or []
        )

        has_retrieval_ground_truth = any(
            [
                (
                    eval_case
                    .expected_document_id
                    is not None
                ),
                (
                    eval_case
                    .expected_chunk_id
                    is not None
                ),
                bool(
                    expected_sources
                ),
            ]
        )

        evaluation_input = (
            EvaluationInput(
                question=
                    eval_case.question,

                retrieved_context=[
                    item.get(
                        "text",
                        "",
                    )
                    for item
                    in retrieval_context
                ],

                expected_context=(
                    [
                        eval_case
                        .expected_text
                    ]
                    if (
                        eval_case
                        .expected_text
                    )
                    else []
                ),

                metadata={
                    "top_k":
                        top_k,

                    "expected_document_id":
                        eval_case
                        .expected_document_id,

                    "expected_chunk_id":
                        eval_case
                        .expected_chunk_id,

                    "expected_sources":
                        expected_sources,

                    "retrieved_document_ids":
                        retrieved_document_ids,

                    "retrieved_document_external_ids":
                        retrieved_document_external_ids,

                    "retrieved_chunk_ids":
                        retrieved_chunk_ids,

                    "has_retrieval_ground_truth":
                        has_retrieval_ground_truth,
                },
            )
        )

        #
        # Hit@K
        #
        hit_evaluator = (
            self.evaluator_registry
            .get(
                "hit_at_k"
            )
        )

        hit_result = (
            hit_evaluator.evaluate(
                evaluation_input
            )
        )

        expected_rank = (
            hit_result
            .metadata
            .get(
                "expected_rank"
            )
        )

        evaluation_input.metadata[
            "expected_rank"
        ] = expected_rank

        #
        # Reciprocal Rank
        #
        rr_evaluator = (
            self.evaluator_registry
            .get(
                "reciprocal_rank"
            )
        )

        rr_result = (
            rr_evaluator.evaluate(
                evaluation_input
            )
        )

        metrics = {
            "hit_at_k": {
                "score":
                    hit_result.score,

                "passed":
                    hit_result.passed,

                "threshold":
                    hit_result.threshold,

                "reason":
                    hit_result.reason,

                "evaluator_type":
                    hit_result
                    .evaluator_type,

                "evaluator_engine":
                    hit_result
                    .evaluator_engine,

                "metadata":
                    hit_result.metadata,
            },

            "reciprocal_rank": {
                "score":
                    rr_result.score,

                "passed":
                    rr_result.passed,

                "threshold":
                    rr_result.threshold,

                "reason":
                    rr_result.reason,

                "evaluator_type":
                    rr_result
                    .evaluator_type,

                "evaluator_engine":
                    rr_result
                    .evaluator_engine,

                "metadata":
                    rr_result.metadata,
            },
        }

        return {
            "retrieved_document_ids":
                retrieved_document_ids,

            "retrieved_document_external_ids":
                retrieved_document_external_ids,

            "retrieved_chunk_ids":
                retrieved_chunk_ids,

            "retrieved_distances":
                retrieved_distances,

            "retrieval_context":
                retrieval_context,

            "expected_rank":
                expected_rank,

            "hit_at_k":
                hit_result.passed,

            "reciprocal_rank":
                rr_result.score,

            "has_retrieval_ground_truth":
                has_retrieval_ground_truth,

            "metrics":
                metrics,
        }

    def aggregate(
        self,
        results: list[dict],
    ) -> dict:
        """
        Aggregate only cases that actually
        have retrieval ground truth.

        Unanswerable/refusal cases without
        expected sources are excluded.
        """

        if not results:
            return {
                "case_count": 0,
                "scored_case_count": 0,
                "unscored_case_count": 0,
                "hit_count": 0,
                "miss_count": 0,
                "hit_rate": 0.0,
                "mrr": 0.0,
            }

        scored_results = [
            result
            for result
            in results
            if (
                result.get(
                    "has_retrieval_ground_truth",
                    False,
                )
            )
        ]

        case_count = len(
            results
        )

        scored_case_count = len(
            scored_results
        )

        unscored_case_count = (
            case_count
            - scored_case_count
        )

        if scored_case_count == 0:
            return {
                "case_count":
                    case_count,

                "scored_case_count":
                    0,

                "unscored_case_count":
                    unscored_case_count,

                "hit_count":
                    0,

                "miss_count":
                    0,

                "hit_rate":
                    0.0,

                "mrr":
                    0.0,
            }

        hit_count = sum(
            1
            for result
            in scored_results
            if (
                result.get(
                    "hit_at_k"
                )
                is True
            )
        )

        miss_count = (
            scored_case_count
            - hit_count
        )

        reciprocal_rank_sum = sum(
            float(
                result.get(
                    "reciprocal_rank"
                )
                or 0.0
            )
            for result
            in scored_results
        )

        hit_rate = (
            hit_count
            / scored_case_count
        )

        mrr = (
            reciprocal_rank_sum
            / scored_case_count
        )

        return {
            "case_count":
                case_count,

            "scored_case_count":
                scored_case_count,

            "unscored_case_count":
                unscored_case_count,

            "hit_count":
                hit_count,

            "miss_count":
                miss_count,

            "hit_rate":
                hit_rate,

            "mrr":
                mrr,
        }