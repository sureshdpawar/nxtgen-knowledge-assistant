from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
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
        self.document_repository = DocumentRepository()
        self.chunk_repository = DocumentChunkRepository()
        self.embedding_repository = DocumentEmbeddingRepository()
        self.chunking_service = DocumentChunkingService()
        self.embedding_service = EmbeddingService()

    def process(
        self,
        db: Session,
        document_id: UUID,
    ) -> dict:

        document = self.document_repository.get(
            db,
            document_id,
        )

        if document is None:
            raise DocumentNotFoundError()

        full_path = (
            Path(settings.DOCUMENT_STORAGE_PATH)
            / document.storage_path
        )

        if not full_path.exists():
            raise FileNotFoundError(
                f"Document not found: {full_path}"
            )

        parser = ParserFactory.get_parser(
            full_path,
        )

        parsed_document = parser.extract(
            full_path,
        )

        chunks = self.chunking_service.chunk(
            parsed_document["pages"],
        )

        self.chunk_repository.delete_by_document_id(
            db=db,
            document_id=document.id,
        )

        for index, chunk in enumerate(chunks):

            document_chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                text=chunk["text"],
                token_count=0,
                chunk_metadata={
                    "page": chunk["page"],
                },
            )

            db.add(document_chunk)

            db.flush()

            embedding = self.embedding_service.embed(
                chunk["text"],
            )

            document_embedding = DocumentEmbedding(
                chunk_id=document_chunk.id,
                embedding=embedding,
            )

            db.add(document_embedding)

        db.commit()

        return {
            "document_id": document.id,
            "chunks_created": len(chunks),
        }