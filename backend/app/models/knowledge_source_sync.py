from datetime import datetime
from uuid import UUID

from huggingface_hub import User
from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.core.enums import (
    KnowledgeSourceSyncStatus,
)
from app.db.base import Base
from app.db.mixins import (
    TimestampMixin,
    UUIDMixin,
)
from app.models.knowledge_source import KnowledgeSource


class KnowledgeSourceSync(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "knowledge_source_sync"

    knowledge_source_id: Mapped[UUID] = (
        mapped_column(
            ForeignKey(
                "knowledge_source.id",
                ondelete="CASCADE",
            ),
            nullable=False,
            index=True,
        )
    )

    triggered_by: Mapped[UUID] = mapped_column(
        ForeignKey(
            "app_user.id",
        ),
        nullable=False,
        index=True,
    )

    status: Mapped[
        KnowledgeSourceSyncStatus
    ] = mapped_column(
        Enum(
            KnowledgeSourceSyncStatus
        ),
        default=(
            KnowledgeSourceSyncStatus.PENDING
        ),
        server_default=(
            KnowledgeSourceSyncStatus.PENDING.value
        ),
        nullable=False,
        index=True,
    )

    started_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=True,
    )

    completed_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=True,
    )

    items_discovered: Mapped[int] = (
        mapped_column(
            Integer,
            default=0,
            server_default="0",
            nullable=False,
        )
    )

    items_new: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )

    items_changed: Mapped[int] = (
        mapped_column(
            Integer,
            default=0,
            server_default="0",
            nullable=False,
        )
    )

    items_unchanged: Mapped[int] = (
        mapped_column(
            Integer,
            default=0,
            server_default="0",
            nullable=False,
        )
    )

    items_missing: Mapped[int] = (
        mapped_column(
            Integer,
            default=0,
            server_default="0",
            nullable=False,
        )
    )

    items_failed: Mapped[int] = (
        mapped_column(
            Integer,
            default=0,
            server_default="0",
            nullable=False,
        )
    )

    error_message: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    provider_summary: Mapped[
        str | None
    ] = mapped_column(
        String(1000),
        nullable=True,
    )

    knowledge_source: Mapped[
        "KnowledgeSource"
    ] = relationship(
        "KnowledgeSource",
        back_populates="syncs",
    )

    trigger_user: Mapped[
        "User"
    ] = relationship(
        "User",
    )