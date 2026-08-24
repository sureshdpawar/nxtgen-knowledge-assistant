from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    ForeignKey,
    Integer,
    JSON,
    String,
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
    from app.models.conversation import (
        Conversation,
    )
    from app.models.conversation_message import (
        ConversationMessage,
    )
    from app.models.knowledge_base import (
        KnowledgeBase,
    )
    from app.models.tenant import (
        Tenant,
    )


class LLMUsageEvent(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "llm_usage_event"

    #
    # Tenant is always required.
    #
    # Every usage event must belong
    # to exactly one tenant.
    #
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

    #
    # Optional dimensions.
    #
    # Some LLM calls may not be tied
    # to a KB, channel or conversation.
    #
    knowledge_base_id: Mapped[
        UUID | None
    ] = mapped_column(
        ForeignKey(
            "knowledge_base.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    chat_channel_id: Mapped[
        UUID | None
    ] = mapped_column(
        ForeignKey(
            "chat_channel.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    conversation_id: Mapped[
        UUID | None
    ] = mapped_column(
        ForeignKey(
            "conversation.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    message_id: Mapped[
        UUID | None
    ] = mapped_column(
        ForeignKey(
            "conversation_message.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    #
    # LLM/provider identity.
    #
    provider: Mapped[
        str
    ] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    model: Mapped[
        str
    ] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    #
    # Allows the same usage system
    # to meter multiple workloads.
    #
    # Examples:
    #
    # chat
    # agent
    # eval
    #
    request_type: Mapped[
        str
    ] = mapped_column(
        String(50),
        nullable=False,
        default="chat",
        server_default="chat",
        index=True,
    )

    #
    # Actual provider-reported usage.
    #
    input_tokens: Mapped[
        int
    ] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    output_tokens: Mapped[
        int
    ] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    total_tokens: Mapped[
        int
    ] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    #
    # Preserve provider-specific
    # usage information without
    # coupling quota logic to it.
    #
    usage_metadata: Mapped[
        dict
    ] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
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

    conversation: Mapped[
        "Conversation | None"
    ] = relationship(
        "Conversation",
    )

    message: Mapped[
        "ConversationMessage | None"
    ] = relationship(
        "ConversationMessage",
    )