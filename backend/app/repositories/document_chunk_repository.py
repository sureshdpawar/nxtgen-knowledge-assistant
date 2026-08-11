from uuid import UUID

from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.repositories.base_repository import BaseRepository


class DocumentChunkRepository(
    BaseRepository[DocumentChunk],
):

    def __init__(self):
        super().__init__(DocumentChunk)

    def delete_by_document_id(
        self,
        db: Session,
        document_id: UUID,
    ) -> None:

        (
            db.query(DocumentChunk)
            .filter(
                DocumentChunk.document_id == document_id,
            )
            .delete(
                synchronize_session=False,
            )
        )