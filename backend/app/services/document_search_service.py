from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.document_embedding_repository import (
    DocumentEmbeddingRepository,
)
from app.services.embedding_service import (
    EmbeddingService,
)


class DocumentSearchService:

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.embedding_repository = (
            DocumentEmbeddingRepository()
        )

    def search(
        self,
        db: Session,
        knowledge_base_id: UUID,
        query: str,
    ):

        query_embedding = self.embedding_service.embed(
            query,
        )

        return self.embedding_repository.search(
            db=db,
            knowledge_base_id=knowledge_base_id,
            query_embedding=query_embedding,
            top_k=settings.TOP_K,
        )