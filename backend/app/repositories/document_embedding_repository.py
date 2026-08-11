from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.document_embedding import DocumentEmbedding
from app.models.knowledge_source import KnowledgeSource
from app.repositories.base_repository import BaseRepository


class DocumentEmbeddingRepository(
    BaseRepository[DocumentEmbedding],
):

    def __init__(self):
        super().__init__(DocumentEmbedding)

    def search(
        self,
        db: Session,
        knowledge_base_id: UUID,
        query_embedding: list[float],
        top_k: int,
    ):

        stmt = (
            select(
                DocumentChunk,
                Document,
                KnowledgeSource,
                DocumentEmbedding.embedding.cosine_distance(
                    query_embedding,
                ).label("score"),
            )
            .join(
                DocumentChunk,
                DocumentEmbedding.chunk_id == DocumentChunk.id,
            )
            .join(
                Document,
                DocumentChunk.document_id == Document.id,
            )
            .join(
                KnowledgeSource,
                Document.knowledge_source_id == KnowledgeSource.id,
            )
            .where(
                KnowledgeSource.knowledge_base_id == knowledge_base_id,
            )
            .order_by(
                DocumentEmbedding.embedding.cosine_distance(
                    query_embedding,
                )
            )
            .limit(
                top_k,
            )
        )

        return db.execute(stmt).all()