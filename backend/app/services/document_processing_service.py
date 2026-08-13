from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import DocumentStatus
from app.exceptions.document import DocumentNotFoundError
from app.models.document_chunk import DocumentChunk
from app.models.document_embedding import DocumentEmbedding
from app.parsers.parser_factory import ParserFactory
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

        try:
            #
            # 1. Mark document as processing
            #
            document.status = (
                DocumentStatus.PROCESSING
            )

            db.commit()
            db.refresh(document)

            #
            # 2. Resolve document path
            #
            full_path = (
                Path(
                    settings.DOCUMENT_STORAGE_PATH,
                )
                / document.storage_path
            )

            if not full_path.exists():
                raise FileNotFoundError(
                    f"Document not found: {full_path}"
                )

            #
            # 3. Parse document
            #
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

            #
            # 4. Chunk document
            #
            chunks = (
                self.chunking_service.chunk(
                    parsed_document[
                        "pages"
                    ],
                )
            )

            #
            # 5. Delete old embeddings FIRST
            #
            self.embedding_repository.delete_by_document_id(
                db=db,
                document_id=document.id,
            )

            #
            # 6. Delete old chunks
            #
            self.chunk_repository.delete_by_document_id(
                db=db,
                document_id=document.id,
            )

            db.flush()

            #
            # 7. Recreate chunks and embeddings
            #
            for index, chunk in enumerate(
                chunks,
            ):

                document_chunk = (
                    DocumentChunk(
                        document_id=
                            document.id,

                        chunk_index=index,

                        text=chunk[
                            "text"
                        ],

                        token_count=0,

                        chunk_metadata={
                            "page":
                                chunk[
                                    "page"
                                ],
                        },
                    )
                )

                db.add(
                    document_chunk,
                )

                db.flush()

                embedding = (
                    self.embedding_service.embed(
                        chunk[
                            "text"
                        ],
                    )
                )

                document_embedding = (
                    DocumentEmbedding(
                        chunk_id=
                            document_chunk.id,

                        embedding=
                            embedding,
                    )
                )

                db.add(
                    document_embedding,
                )

            #
            # 8. Mark document as ready
            #
            document.status = (
                DocumentStatus.READY
            )

            db.commit()
            db.refresh(document)

            return {
                "document_id":
                    document.id,

                "chunks_created":
                    len(chunks),

                "status":
                    document.status.value,
            }

        except Exception:
            #
            # Roll back processing work
            #
            db.rollback()

            #
            # Reload document in a clean transaction
            #
            document = (
                self.document_repository.get(
                    db,
                    document_id,
                )
            )

            #
            # Mark document failed
            #
            if document is not None:
                document.status = (
                    DocumentStatus.FAILED
                )

                db.commit()

            raise