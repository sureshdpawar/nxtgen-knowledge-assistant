from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.models.document_embedding import DocumentEmbedding
from app.repositories.base_repository import BaseRepository


class DocumentEmbeddingRepository(
    BaseRepository[DocumentEmbedding],
):

    def __init__(self):
        super().__init__(
            DocumentEmbedding,
        )

    def delete_by_document_id(
        self,
        db: Session,
        document_id: UUID,
    ) -> None:

        chunk_ids = (
            select(
                DocumentChunk.id,
            )
            .where(
                DocumentChunk.document_id
                == document_id,
            )
        )

        stmt = (
            delete(
                DocumentEmbedding,
            )
            .where(
                DocumentEmbedding.chunk_id.in_(
                    chunk_ids,
                ),
            )
        )

        db.execute(stmt)

        db.flush()