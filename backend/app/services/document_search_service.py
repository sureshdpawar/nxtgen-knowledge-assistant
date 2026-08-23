import logging
import time

from uuid import UUID

from sqlalchemy.orm import Session

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

        if (
            top_k_override is not None
            and top_k_override < 1
        ):
            raise ValueError(
                "top_k_override must be at least 1"
            )

        # Normal production calls inherit the KB/platform setting.
        # Evaluation can explicitly request a K without mutating the KB.
        top_k = (
            top_k_override
            if top_k_override is not None
            else knowledge_base.effective_top_k
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
                top_k=
                    top_k,
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
            top_k,
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
                "top_k=%s "
                "total_ms=%.2f",
                knowledge_base_id,
                top_k,
                total_elapsed_ms,
            )

        return results
