from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Enum,
    ForeignKey,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.core.enums import DocumentStatus
from app.db.base import Base
from app.db.mixins import (
    TimestampMixin,
    UUIDMixin,
)


class Document(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "document"

    knowledge_source_id: Mapped[UUID] = mapped_column(
        ForeignKey("knowledge_source.id"),
        nullable=False,
        index=True,
    )

    uploaded_by: Mapped[UUID] = mapped_column(
        ForeignKey("app_user.id"),
        nullable=False,
        index=True,
    )

    original_filename: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    stored_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    mime_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    checksum: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    storage_path: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    external_id: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        index=True,
    )

    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus),
        default=DocumentStatus.PENDING,
        server_default=DocumentStatus.PENDING.value,
        nullable=False,
    )

    knowledge_source: Mapped["KnowledgeSource"] = relationship(
        "KnowledgeSource",
        back_populates="documents",
    )

    uploader: Mapped["User"] = relationship(
        "User",
    )

    chunks: Mapped[list["DocumentChunk"]] = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )

    ingestion_jobs: Mapped[list["DocumentIngestionJob"]] = relationship(
        "DocumentIngestionJob",
        back_populates="document",
        cascade="all, delete-orphan",
    )
