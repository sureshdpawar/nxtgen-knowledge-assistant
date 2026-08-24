from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base
from app.db.mixins import (
    TimestampMixin,
    UUIDMixin,
)

if TYPE_CHECKING:
    from app.models.chat_channel import (
        ChatChannel,
    )
    from app.models.knowledge_base import (
        KnowledgeBase,
    )
    from app.models.tenant import (
        Tenant,
    )


class UsageLimit(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "usage_limit"

    __table_args__ = (
        #
        # Valid scopes:
        #
        # Tenant:
        #   tenant_id
        #
        # Knowledge Base:
        #   tenant_id + knowledge_base_id
        #
        # Channel:
        #   tenant_id
        #   + knowledge_base_id
        #   + chat_channel_id
        #
        CheckConstraint(
            "("
            "knowledge_base_id IS NULL "
            "AND chat_channel_id IS NULL"
            ") "
            "OR "
            "("
            "knowledge_base_id IS NOT NULL "
            "AND chat_channel_id IS NULL"
            ") "
            "OR "
            "("
            "knowledge_base_id IS NOT NULL "
            "AND chat_channel_id IS NOT NULL"
            ")",
            name="ck_usage_limit_scope",
        ),

        #
        # Only one tenant-level quota
        # configuration per tenant.
        #
        Index(
            "uq_usage_limit_tenant_scope",
            "tenant_id",
            unique=True,
            postgresql_where=text(
                "knowledge_base_id IS NULL "
                "AND chat_channel_id IS NULL"
            ),
        ),

        #
        # Only one KB-level quota
        # configuration per KB.
        #
        Index(
            "uq_usage_limit_kb_scope",
            "knowledge_base_id",
            unique=True,
            postgresql_where=text(
                "knowledge_base_id IS NOT NULL "
                "AND chat_channel_id IS NULL"
            ),
        ),

        #
        # Only one channel-level quota
        # configuration per channel.
        #
        Index(
            "uq_usage_limit_channel_scope",
            "chat_channel_id",
            unique=True,
            postgresql_where=text(
                "chat_channel_id IS NOT NULL"
            ),
        ),
    )

    tenant_id: Mapped[
        UUID
    ] = mapped_column(
        ForeignKey(
            "tenant.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    knowledge_base_id: Mapped[
        UUID | None
    ] = mapped_column(
        ForeignKey(
            "knowledge_base.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    chat_channel_id: Mapped[
        UUID | None
    ] = mapped_column(
        ForeignKey(
            "chat_channel.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    #
    # Daily limits.
    #
    # NULL = no limit configured
    # 0    = no usage allowed
    #
    daily_message_limit: Mapped[
        int | None
    ] = mapped_column(
        Integer,
        nullable=True,
    )

    daily_input_token_limit: Mapped[
        int | None
    ] = mapped_column(
        Integer,
        nullable=True,
    )

    daily_output_token_limit: Mapped[
        int | None
    ] = mapped_column(
        Integer,
        nullable=True,
    )

    daily_total_token_limit: Mapped[
        int | None
    ] = mapped_column(
        Integer,
        nullable=True,
    )

    #
    # Monthly limits.
    #
    monthly_message_limit: Mapped[
        int | None
    ] = mapped_column(
        Integer,
        nullable=True,
    )

    monthly_input_token_limit: Mapped[
        int | None
    ] = mapped_column(
        Integer,
        nullable=True,
    )

    monthly_output_token_limit: Mapped[
        int | None
    ] = mapped_column(
        Integer,
        nullable=True,
    )

    monthly_total_token_limit: Mapped[
        int | None
    ] = mapped_column(
        Integer,
        nullable=True,
    )

    #
    # Per-request safety limits.
    #
    max_input_tokens_per_request: Mapped[
        int | None
    ] = mapped_column(
        Integer,
        nullable=True,
    )

    max_output_tokens_per_request: Mapped[
        int | None
    ] = mapped_column(
        Integer,
        nullable=True,
    )

    #
    # Controls the daily/monthly
    # quota windows.
    #
    # Example:
    #
    # Asia/Kolkata
    # America/New_York
    # UTC
    #
    timezone: Mapped[
        str
    ] = mapped_column(
        String(100),
        nullable=False,
        default="UTC",
        server_default="UTC",
    )

    #
    # Administrative kill switch.
    #
    # False means chat is blocked
    # for this scope regardless of
    # remaining quota.
    #
    enabled: Mapped[
        bool
    ] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text(
            "true"
        ),
    )

    tenant: Mapped[
        "Tenant"
    ] = relationship(
        "Tenant",
    )

    knowledge_base: Mapped[
        "KnowledgeBase | None"
    ] = relationship(
        "KnowledgeBase",
    )

    chat_channel: Mapped[
        "ChatChannel | None"
    ] = relationship(
        "ChatChannel",
    )