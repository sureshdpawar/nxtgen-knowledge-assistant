from uuid import UUID

from sqlalchemy import ForeignKey, Integer, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin


class DocumentChunk(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "document_chunk"

    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("document.id"),
        nullable=False,
        index=True,
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    token_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    chunk_metadata: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="chunks",
    )