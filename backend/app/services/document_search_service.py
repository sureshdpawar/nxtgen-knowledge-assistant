import logging
import time

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.document_embedding_repository import (
    DocumentEmbeddingRepository,
)
from app.services.embedding_service import (
    EmbeddingService,
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

    def search(
        self,
        db: Session,
        knowledge_base_id: UUID,
        query: str,
    ):
        started_at = (
            time.perf_counter()
        )

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

        repository_started_at = (
            time.perf_counter()
        )

        results = (
            self.embedding_repository.search(
                db=db,
                knowledge_base_id=
                    knowledge_base_id,
                query_embedding=
                    query_embedding,
                top_k=settings.TOP_K,
            )
        )

        repository_elapsed_ms = (
            (
                time.perf_counter()
                - repository_started_at
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
            "results=%s "
            "top_k=%s "
            "embedding_ms=%.2f "
            "repository_ms=%.2f "
            "total_ms=%.2f",
            knowledge_base_id,
            len(results),
            settings.TOP_K,
            embedding_elapsed_ms,
            repository_elapsed_ms,
            total_elapsed_ms,
        )

        if (
            total_elapsed_ms
            > 1000
        ):
            logger.warning(
                "Slow KB search "
                "kb=%s "
                "total_ms=%.2f",
                knowledge_base_id,
                total_elapsed_ms,
            )

        return results