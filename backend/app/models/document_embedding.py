from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.core.config import settings
from app.db.base import Base
from app.db.mixins import (
    TimestampMixin,
    UUIDMixin,
)


class DocumentEmbedding(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = (
        "document_embedding"
    )

    chunk_id: Mapped[UUID] = (
        mapped_column(
            ForeignKey(
                "document_chunk.id"
            ),
            nullable=False,
            unique=True,
            index=True,
        )
    )

    embedding_model: Mapped[str] = (
        mapped_column(
            String(255),
            default=lambda: (
                settings.EMBEDDING_MODEL
            ),
            nullable=False,
        )
    )

    embedding: Mapped[
        list[float]
    ] = mapped_column(
        Vector(
            settings
            .EMBEDDING_DIMENSIONS
        ),
        nullable=False,
    )

    chunk: Mapped[
        "DocumentChunk"
    ] = relationship(
        "DocumentChunk",
        back_populates="embedding",
    )