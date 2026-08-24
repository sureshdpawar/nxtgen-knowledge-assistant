from uuid import UUID

from sqlalchemy.orm import Session

from app.models.eval_case import (
    EvalCase,
)
from app.services.document_search_service import (
    DocumentSearchService,
)


class RetrievalEvalService:

    def __init__(self):
        self.search_service = (
            DocumentSearchService()
        )

    def evaluate_case(
        self,
        db: Session,
        knowledge_base_id: UUID,
        eval_case: EvalCase,
        top_k: int,
    ) -> dict:
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
        retrieved_chunk_ids = []
        retrieved_distances = []
        retrieval_context = []

        expected_rank = None

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

            chunk_id = str(
                chunk.id
            )

            retrieved_document_ids.append(
                document_id
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
                    "rank": rank,
                    "document_id":
                        document_id,
                    "chunk_id":
                        chunk_id,
                    "document_name":
                        document.original_filename,
                    "chunk_index":
                        chunk.chunk_index,
                    "text":
                        chunk.text,
                    "distance":
                        float(
                            distance
                        ),
                }
            )

            if (
                eval_case
                .expected_document_id
                is not None
                and document.id
                == eval_case
                .expected_document_id
                and expected_rank
                is None
            ):
                expected_rank = rank

        #
        # Retrieval metrics.
        #
        # For Eval v1 we score against
        # expected_document_id.
        #
        # If the expected document appears
        # anywhere inside the top K results:
        #
        #     Hit@K = True
        #
        # Reciprocal Rank:
        #
        #     rank 1 -> 1.0
        #     rank 2 -> 0.5
        #     rank 3 -> 0.333...
        #
        hit_at_k = (
            expected_rank is not None
        )

        reciprocal_rank = (
            1.0 / expected_rank
            if expected_rank
            is not None
            else 0.0
        )

        return {
            "retrieved_document_ids":
                retrieved_document_ids,

            "retrieved_chunk_ids":
                retrieved_chunk_ids,

            "retrieved_distances":
                retrieved_distances,

            "retrieval_context":
                retrieval_context,

            "expected_rank":
                expected_rank,

            "hit_at_k":
                hit_at_k,

            "reciprocal_rank":
                reciprocal_rank,
        }

    def aggregate(
        self,
        results: list[dict],
    ) -> dict:
        if not results:
            return {
                "case_count": 0,
                "hit_count": 0,
                "hit_rate": 0.0,
                "mrr": 0.0,
            }

        case_count = len(
            results
        )

        hit_count = sum(
            1
            for result in results
            if result[
                "hit_at_k"
            ]
        )

        reciprocal_rank_sum = sum(
            result[
                "reciprocal_rank"
            ]
            for result in results
        )

        hit_rate = (
            hit_count
            / case_count
        )

        mrr = (
            reciprocal_rank_sum
            / case_count
        )

        return {
            "case_count":
                case_count,

            "hit_count":
                hit_count,

            "hit_rate":
                hit_rate,

            "mrr":
                mrr,
        }