import logging
import time

from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import DocumentStatus
from app.exceptions.document import (
    DocumentNotFoundError,
)
from app.models.document_chunk import (
    DocumentChunk,
)
from app.models.document_embedding import (
    DocumentEmbedding,
)
from app.parsers.parser_factory import (
    ParserFactory,
)
from app.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)
from app.repositories.document_embedding_repository import (
    DocumentEmbeddingRepository,
)
from app.repositories.document_repository import (
    DocumentRepository,
)
from app.services.document_chunking_service import (
    DocumentChunkingService,
)
from app.services.embedding_service import (
    EmbeddingService,
)


logger = logging.getLogger(
    "nxtgen.document_processing"
)


class DocumentProcessingService:

    def __init__(self):
        self.document_repository = (
            DocumentRepository()
        )

        self.chunk_repository = (
            DocumentChunkRepository()
        )

        self.embedding_repository = (
            DocumentEmbeddingRepository()
        )

        self.chunking_service = (
            DocumentChunkingService()
        )

        self.embedding_service = (
            EmbeddingService()
        )

    def _sanitize_text(
        self,
        text: str,
    ) -> str:
        return (
            text
            .replace(
                "\x00",
                "",
            )
            .strip()
        )

    def _is_usable_text(
        self,
        text: str,
    ) -> bool:
        if not text:
            return False

        alphanumeric_count = sum(
            character.isalnum()
            for character in text
        )

        alphanumeric_ratio = (
            alphanumeric_count
            / max(
                len(text),
                1,
            )
        )

        return (
            alphanumeric_ratio
            >= 0.15
        )

    def process(
        self,
        db: Session,
        document_id: UUID,
    ) -> dict:

        document = (
            self.document_repository.get(
                db,
                document_id,
            )
        )

        if document is None:
            raise DocumentNotFoundError()

        started_at = (
            time.perf_counter()
        )

        try:
            document.status = (
                DocumentStatus.PROCESSING
            )

            db.commit()
            db.refresh(
                document,
            )

            logger.info(
                "Document processing started "
                "document=%s",
                document.id,
            )

            full_path = (
                Path(
                    settings.DOCUMENT_STORAGE_PATH,
                )
                / document.storage_path
            )

            if not full_path.exists():
                raise FileNotFoundError(
                    f"Document not found: "
                    f"{full_path}"
                )

            parse_started_at = (
                time.perf_counter()
            )

            parser = (
                ParserFactory.get_parser(
                    full_path,
                )
            )

            parsed_document = (
                parser.extract(
                    full_path,
                )
            )

            parse_elapsed_ms = (
                (
                    time.perf_counter()
                    - parse_started_at
                )
                * 1000
            )

            pages = (
                parsed_document.get(
                    "pages",
                    [],
                )
            )

            if not pages:
                raise ValueError(
                    "Document contains "
                    "no parsable pages."
                )

            chunk_started_at = (
                time.perf_counter()
            )

            raw_chunks = (
                self.chunking_service.chunk(
                    pages,
                )
            )

            chunk_elapsed_ms = (
                (
                    time.perf_counter()
                    - chunk_started_at
                )
                * 1000
            )

            if not raw_chunks:
                raise ValueError(
                    "Document produced "
                    "no searchable chunks."
                )

            chunks = []

            skipped_chunks = 0

            for chunk in raw_chunks:
                raw_text = (
                    chunk.get(
                        "text",
                        "",
                    )
                )

                clean_text = (
                    self._sanitize_text(
                        raw_text,
                    )
                )

                if not self._is_usable_text(
                    clean_text,
                ):
                    skipped_chunks += 1
                    continue

                chunks.append(
                    {
                        **chunk,
                        "text":
                            clean_text,
                    }
                )

            if not chunks:
                raise ValueError(
                    "Document produced "
                    "no usable searchable chunks."
                )

            if skipped_chunks > 0:
                logger.warning(
                    "Skipped unusable chunks "
                    "document=%s "
                    "skipped=%s "
                    "usable=%s",
                    document.id,
                    skipped_chunks,
                    len(chunks),
                )

            texts = [
                chunk["text"]
                for chunk in chunks
            ]

            embedding_started_at = (
                time.perf_counter()
            )

            embeddings = (
                self.embedding_service
                .embed_batch(
                    texts,
                )
            )

            embedding_elapsed_ms = (
                (
                    time.perf_counter()
                    - embedding_started_at
                )
                * 1000
            )

            self.embedding_repository.delete_by_document_id(
                db=db,
                document_id=document.id,
            )

            self.chunk_repository.delete_by_document_id(
                db=db,
                document_id=document.id,
            )

            db.flush()

            for (
                index,
                chunk,
            ) in enumerate(
                chunks,
            ):
                document_chunk = (
                    DocumentChunk(
                        document_id=
                            document.id,

                        chunk_index=
                            index,

                        text=
                            chunk[
                                "text"
                            ],

                        token_count=
                            0,

                        chunk_metadata={
                            "page":
                                chunk.get(
                                    "page",
                                    1,
                                ),
                        },
                    )
                )

                db.add(
                    document_chunk,
                )

                db.flush()

                document_embedding = (
                    DocumentEmbedding(
                        chunk_id=
                            document_chunk.id,

                        embedding=
                            embeddings[
                                index
                            ],
                    )
                )

                db.add(
                    document_embedding,
                )

            document.status = (
                DocumentStatus.READY
            )

            db.commit()
            db.refresh(
                document,
            )

            total_elapsed_ms = (
                (
                    time.perf_counter()
                    - started_at
                )
                * 1000
            )

            logger.info(
                "Document processing completed "
                "document=%s "
                "raw_chunks=%s "
                "chunks=%s "
                "skipped=%s "
                "parse_ms=%.2f "
                "chunk_ms=%.2f "
                "embedding_ms=%.2f "
                "total_ms=%.2f",
                document.id,
                len(raw_chunks),
                len(chunks),
                skipped_chunks,
                parse_elapsed_ms,
                chunk_elapsed_ms,
                embedding_elapsed_ms,
                total_elapsed_ms,
            )

            return {
                "document_id":
                    document.id,

                "chunks_created":
                    len(chunks),

                "chunks_skipped":
                    skipped_chunks,

                "status":
                    document.status.value,
            }

        except Exception as exc:
            db.rollback()

            logger.exception(
                "Document processing failed "
                "document=%s "
                "error_type=%s",
                document_id,
                type(exc).__name__,
            )

            document = (
                self.document_repository.get(
                    db,
                    document_id,
                )
            )

            if document is not None:
                document.status = (
                    DocumentStatus.FAILED
                )

                db.commit()

            raise