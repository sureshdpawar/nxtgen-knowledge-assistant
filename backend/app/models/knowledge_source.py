from datetime import datetime
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import (
    KnowledgeSourceStatus,
    KnowledgeSourceType,
)
from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin


class KnowledgeSource(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "knowledge_source"

    knowledge_base_id: Mapped[UUID] = mapped_column(
        ForeignKey("knowledge_base.id"),
        nullable=False,
        index=True,
    )

    created_by: Mapped[UUID] = mapped_column(
        ForeignKey("app_user.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    type: Mapped[KnowledgeSourceType] = mapped_column(
        Enum(KnowledgeSourceType),
        nullable=False,
    )

    status: Mapped[KnowledgeSourceStatus] = mapped_column(
        Enum(KnowledgeSourceStatus),
        default=KnowledgeSourceStatus.ACTIVE,
        server_default=KnowledgeSourceStatus.ACTIVE.value,
        nullable=False,
    )

    configuration: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    last_sync_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    knowledge_base: Mapped["KnowledgeBase"] = relationship(
    "KnowledgeBase",
    back_populates="knowledge_sources",
    )

    creator: Mapped["User"] = relationship(
        "User",
        back_populates="knowledge_sources",
    )

    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="knowledge_source",
        cascade="all, delete-orphan",
    )