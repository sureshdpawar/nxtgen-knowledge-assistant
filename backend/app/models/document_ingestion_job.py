from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import DocumentIngestionJobStatus
from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin


class DocumentIngestionJob(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "document_ingestion_job"

    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("document.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[DocumentIngestionJobStatus] = mapped_column(
        Enum(DocumentIngestionJobStatus),
        default=DocumentIngestionJobStatus.PENDING,
        server_default=DocumentIngestionJobStatus.PENDING.value,
        nullable=False,
        index=True,
    )

    attempt_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )

    max_attempts: Mapped[int] = mapped_column(
        Integer,
        default=3,
        server_default="3",
        nullable=False,
    )

    available_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    claimed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    failed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    worker_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="ingestion_jobs",
    )
