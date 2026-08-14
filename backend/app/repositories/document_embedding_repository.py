from uuid import UUID

from sqlalchemy import (
    delete,
    select,
)
from sqlalchemy.orm import Session

from app.core.enums import (
    DocumentStatus,
)
from app.models.document import (
    Document,
)
from app.models.document_chunk import (
    DocumentChunk,
)
from app.models.document_embedding import (
    DocumentEmbedding,
)
from app.models.knowledge_source import (
    KnowledgeSource,
)
from app.repositories.base_repository import (
    BaseRepository,
)


class DocumentEmbeddingRepository(
    BaseRepository[
        DocumentEmbedding
    ],
):

    def __init__(self):
        super().__init__(
            DocumentEmbedding,
        )

    def search(
        self,
        db: Session,
        knowledge_base_id: UUID,
        query_embedding:
            list[float],
        top_k: int = 5,
    ):
        distance = (
            DocumentEmbedding
            .embedding
            .cosine_distance(
                query_embedding,
            )
        )

        stmt = (
            select(
                DocumentChunk,
                Document,
                KnowledgeSource,
                distance.label(
                    "distance",
                ),
            )
            .join(
                DocumentEmbedding,
                DocumentEmbedding.chunk_id
                == DocumentChunk.id,
            )
            .join(
                Document,
                Document.id
                == DocumentChunk.document_id,
            )
            .join(
                KnowledgeSource,
                KnowledgeSource.id
                == Document.knowledge_source_id,
            )
            .where(
                KnowledgeSource
                .knowledge_base_id
                == knowledge_base_id,

                Document.status
                == DocumentStatus.READY,
            )
            .order_by(
                distance,
            )
            .limit(
                top_k,
            )
        )

        return list(
            db.execute(
                stmt,
            ).all()
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
                DocumentEmbedding
                .chunk_id
                .in_(
                    chunk_ids,
                ),
            )
        )

        db.execute(
            stmt,
        )

        db.flush()