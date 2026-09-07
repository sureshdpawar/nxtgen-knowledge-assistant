import logging
import time

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.telemetry import (
    get_tracer,
)
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

tracer = get_tracer(
    __name__
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

        with tracer.start_as_current_span(
            "rag.retrieval"
        ) as retrieval_span:
            retrieval_span.set_attribute(
                "knowgentiq.knowledge_base.id",
                str(
                    knowledge_base_id
                ),
            )

            knowledge_base = (
                db.get(
                    KnowledgeBase,
                    knowledge_base_id,
                )
            )

            if knowledge_base is None:
                retrieval_span.set_attribute(
                    "knowgentiq.retrieval."
                    "knowledge_base_found",
                    False,
                )

                raise (
                    KnowledgeBaseNotFoundError()
                )

            retrieval_span.set_attribute(
                "knowgentiq.retrieval."
                "knowledge_base_found",
                True,
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

            reranking_enabled = (
                knowledge_base
                .effective_reranking_enabled
            )

            #
            # Only broaden vector retrieval
            # when those extra candidates
            # will actually be reranked.
            #
            candidate_top_k = (
                self._candidate_top_k(
                    final_top_k,
                )
                if reranking_enabled
                else final_top_k
            )

            retrieval_span.set_attribute(
                "knowgentiq.retrieval."
                "final_top_k",
                final_top_k,
            )

            retrieval_span.set_attribute(
                "knowgentiq.retrieval."
                "candidate_top_k",
                candidate_top_k,
            )

            retrieval_span.set_attribute(
                "knowgentiq.retrieval."
                "top_k_overridden",
                (
                    top_k_override
                    is not None
                ),
            )

            retrieval_span.set_attribute(
                "knowgentiq.reranker."
                "enabled",
                reranking_enabled,
            )

            #
            # Stage 1:
            # Embed the user query.
            #
            embedding_started_at = (
                time.perf_counter()
            )

            with (
                tracer
                .start_as_current_span(
                    "rag.embedding"
                )
            ) as embedding_span:
                embedding_span.set_attribute(
                    "knowgentiq.embedding."
                    "model",
                    settings.EMBEDDING_MODEL,
                )

                embedding_span.set_attribute(
                    "knowgentiq.embedding."
                    "dimensions",
                    (
                        settings
                        .EMBEDDING_DIMENSIONS
                    ),
                )

                #
                # Privacy:
                # Do not attach query text.
                #
                embedding_span.set_attribute(
                    "knowgentiq.embedding."
                    "input_present",
                    bool(
                        query
                    ),
                )

                query_embedding = (
                    self.embedding_service
                    .embed(
                        query,
                    )
                )

                embedding_span.set_attribute(
                    "knowgentiq.embedding."
                    "output_dimensions",
                    len(
                        query_embedding
                    ),
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
            # Retrieve either the final
            # Top-K directly or a broader
            # reranking candidate set.
            #
            repository_started_at = (
                time.perf_counter()
            )

            with (
                tracer
                .start_as_current_span(
                    "rag.vector_search"
                )
            ) as vector_span:
                vector_span.set_attribute(
                    "knowgentiq.knowledge_base.id",
                    str(
                        knowledge_base_id
                    ),
                )

                vector_span.set_attribute(
                    "knowgentiq.vector_search."
                    "top_k",
                    candidate_top_k,
                )

                candidates = (
                    self.embedding_repository
                    .search(
                        db=db,
                        knowledge_base_id=
                            knowledge_base_id,
                        query_embedding=
                            query_embedding,
                        top_k=
                            candidate_top_k,
                    )
                )

                vector_span.set_attribute(
                    "knowgentiq.vector_search."
                    "candidate_count",
                    len(
                        candidates
                    ),
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
            # Rerank only when enabled for
            # this knowledge base.
            #
            reranker_elapsed_ms = 0.0

            if reranking_enabled:
                reranker_started_at = (
                    time.perf_counter()
                )

                with (
                    tracer
                    .start_as_current_span(
                        "rag.reranking"
                    )
                ) as reranker_span:
                    reranker_span.set_attribute(
                        "knowgentiq.reranker."
                        "enabled",
                        True,
                    )

                    reranker_span.set_attribute(
                        "knowgentiq.reranker."
                        "model",
                        settings.RERANKER_MODEL,
                    )

                    reranker_span.set_attribute(
                        "knowgentiq.reranker."
                        "candidate_count",
                        len(
                            candidates
                        ),
                    )

                    reranker_span.set_attribute(
                        "knowgentiq.reranker."
                        "top_k",
                        final_top_k,
                    )

                    results = (
                        self.reranker_service
                        .rerank(
                            query=query,
                            candidates=candidates,
                            top_k=final_top_k,
                        )
                    )

                    reranker_span.set_attribute(
                        "knowgentiq.reranker."
                        "result_count",
                        len(
                            results
                        ),
                    )

                reranker_elapsed_ms = (
                    (
                        time.perf_counter()
                        - reranker_started_at
                    )
                    * 1000
                )

            else:
                #
                # Vector search already used
                # final_top_k, so no extra
                # ranking work is needed.
                #
                results = (
                    candidates[
                        :final_top_k
                    ]
                )

            total_elapsed_ms = (
                (
                    time.perf_counter()
                    - started_at
                )
                * 1000
            )

            retrieval_span.set_attribute(
                "knowgentiq.retrieval."
                "candidate_count",
                len(
                    candidates
                ),
            )

            retrieval_span.set_attribute(
                "knowgentiq.retrieval."
                "result_count",
                len(
                    results
                ),
            )

            retrieval_span.set_attribute(
                "knowgentiq.retrieval."
                "duration_ms",
                total_elapsed_ms,
            )

            logger.info(
                "KB search completed "
                "kb=%s "
                "reranking_enabled=%s "
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
                reranking_enabled,
                len(
                    candidates
                ),
                len(
                    results
                ),
                candidate_top_k,
                final_top_k,
                top_k_override,
                settings.EMBEDDING_MODEL,
                (
                    settings
                    .EMBEDDING_DIMENSIONS
                ),
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
                    "reranking_enabled=%s "
                    "candidate_top_k=%s "
                    "final_top_k=%s "
                    "reranker_model='%s' "
                    "total_ms=%.2f",
                    knowledge_base_id,
                    reranking_enabled,
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
