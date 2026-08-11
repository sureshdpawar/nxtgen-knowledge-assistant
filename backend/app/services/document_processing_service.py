from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.exceptions.document import DocumentNotFoundError
from app.models.document_chunk import DocumentChunk
from app.parsers.parser_factory import ParserFactory
from app.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)
from app.repositories.document_repository import (
    DocumentRepository,
)
from app.services.document_chunking_service import (
    DocumentChunkingService,
)


class DocumentProcessingService:

    def __init__(self):
        self.document_repository = DocumentRepository()
        self.chunk_repository = DocumentChunkRepository()
        self.chunking_service = DocumentChunkingService()

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
            parsed_document["text"],
        )

        self.chunk_repository.delete_by_document_id(
            db=db,
            document_id=document.id,
        )

        for index, chunk_text in enumerate(chunks):

            document_chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                text=chunk_text,
                token_count=0,
                chunk_metadata={},
            )

            db.add(document_chunk)

        db.commit()

        return {
            "document_id": str(document.id),
            "chunks_created": len(chunks),
        }