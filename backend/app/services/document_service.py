from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.repositories.document_repository import (
    DocumentRepository,
)


class DocumentService:

    def __init__(self):
        self.repository = (
            DocumentRepository()
        )

    def get_document(
        self,
        db: Session,
        document_id: UUID,
    ) -> Document | None:

        return self.repository.get(
            db,
            document_id,
        )

    def list_by_knowledge_source(
        self,
        db: Session,
        knowledge_source_id: UUID,
    ) -> list[Document]:

        stmt = (
            select(Document)
            .where(
                Document.knowledge_source_id
                == knowledge_source_id,
            )
            .order_by(
                Document.created_at.desc(),
            )
        )

        return list(
            db.scalars(stmt).all()
        )

    def delete_document(
        self,
        db: Session,
        document_id: UUID,
    ) -> bool:

        document = self.get_document(
            db=db,
            document_id=document_id,
        )

        if document is None:
            return False

        db.delete(document)
        db.commit()

        return True