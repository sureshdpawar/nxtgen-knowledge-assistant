import logging
import time

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.exceptions.knowledge_base import (
    KnowledgeBaseNotFoundError,
)
from app.models.knowledge_base import (
    KnowledgeBase,
)
from app.repositories.document_embedding_repository import (
    DocumentEmbeddingRepository,
)
from app.services.embedding_service import (
    EmbeddingService,
)
from app.services.reranker_service import (
    RerankerService,
)


logger = logging.getLogger(
    "nxtgen.search"
)


class DocumentSearchService:

    def __init__(self):
        self.embedding_service = (
            EmbeddingService()
        )

        self.embedding_repository = (
            DocumentEmbeddingRepository()
        )

        self.reranker_service = (
            RerankerService()
        )

    def search(
        self,
        db: Session,
        knowledge_base_id: UUID,
        query: str,
        top_k_override: int | None = None,
    ):
        started_at = (
            time.perf_counter()
        )

        knowledge_base = (
            db.get(
                KnowledgeBase,
                knowledge_base_id,
            )
        )

        if knowledge_base is None:
            raise (
                KnowledgeBaseNotFoundError()
            )

        final_top_k = (
            top_k_override
            if top_k_override
            is not None
            else knowledge_base
            .effective_top_k
        )

        if final_top_k < 1:
            raise ValueError(
                "top_k must be "
                "greater than 0."
            )

        candidate_top_k = (
            self._candidate_top_k(
                final_top_k,
            )
        )

        #
        # Stage 1:
        # Embed the user query.
        #
        embedding_started_at = (
            time.perf_counter()
        )

        query_embedding = (
            self.embedding_service.embed(
                query,
            )
        )

        embedding_elapsed_ms = (
            (
                time.perf_counter()
                - embedding_started_at
            )
            * 1000
        )

        #
        # Stage 2:
        # Retrieve a broader candidate set
        # from pgvector.
        #
        repository_started_at = (
            time.perf_counter()
        )

        candidates = (
            self.embedding_repository.search(
                db=db,
                knowledge_base_id=
                    knowledge_base_id,
                query_embedding=
                    query_embedding,
                top_k=
                    candidate_top_k,
            )
        )

        repository_elapsed_ms = (
            (
                time.perf_counter()
                - repository_started_at
            )
            * 1000
        )

        #
        # Stage 3:
        # Rerank vector candidates using
        # the configured cross-encoder.
        #
        reranker_started_at = (
            time.perf_counter()
        )

        results = (
            self.reranker_service.rerank(
                query=query,
                candidates=candidates,
                top_k=final_top_k,
            )
        )

        reranker_elapsed_ms = (
            (
                time.perf_counter()
                - reranker_started_at
            )
            * 1000
        )

        total_elapsed_ms = (
            (
                time.perf_counter()
                - started_at
            )
            * 1000
        )

        logger.info(
            "KB search completed "
            "kb=%s "
            "candidates=%s "
            "results=%s "
            "candidate_top_k=%s "
            "final_top_k=%s "
            "top_k_override=%s "
            "embedding_model='%s' "
            "embedding_dimensions=%s "
            "reranker_model='%s' "
            "embedding_ms=%.2f "
            "repository_ms=%.2f "
            "reranker_ms=%.2f "
            "total_ms=%.2f",
            knowledge_base_id,
            len(candidates),
            len(results),
            candidate_top_k,
            final_top_k,
            top_k_override,
            settings.EMBEDDING_MODEL,
            settings.EMBEDDING_DIMENSIONS,
            settings.RERANKER_MODEL,
            embedding_elapsed_ms,
            repository_elapsed_ms,
            reranker_elapsed_ms,
            total_elapsed_ms,
        )

        if total_elapsed_ms > 1000:
            logger.warning(
                "Slow KB search "
                "kb=%s "
                "candidate_top_k=%s "
                "final_top_k=%s "
                "reranker_model='%s' "
                "total_ms=%.2f",
                knowledge_base_id,
                candidate_top_k,
                final_top_k,
                settings.RERANKER_MODEL,
                total_elapsed_ms,
            )

        return results

    @staticmethod
    def _candidate_top_k(
        final_top_k: int,
    ) -> int:
        candidate_top_k = max(
            final_top_k,
            final_top_k
            * settings
            .RERANKER_CANDIDATE_MULTIPLIER,
        )

        return min(
            candidate_top_k,
            settings
            .RERANKER_MAX_CANDIDATES,
        )