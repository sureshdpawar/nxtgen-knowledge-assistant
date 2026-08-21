from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Enum,
    ForeignKey,
    JSON,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.core.enums import (
    ChatChannelStatus,
    ChatChannelType,
)
from app.db.base import Base
from app.db.mixins import (
    TimestampMixin,
    UUIDMixin,
)

if TYPE_CHECKING:
    from app.models.chat_channel_api_key import (
        ChatChannelApiKey,
    )
    from app.models.conversation import (
        Conversation,
    )
    from app.models.knowledge_base import (
        KnowledgeBase,
    )
    from app.models.tenant import (
        Tenant,
    )


class ChatChannel(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "chat_channel"

    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenant.id"),
        nullable=False,
        index=True,
    )

    knowledge_base_id: Mapped[UUID] = mapped_column(
        ForeignKey("knowledge_base.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    type: Mapped[
        ChatChannelType
    ] = mapped_column(
        Enum(ChatChannelType),
        nullable=False,
        index=True,
    )

    status: Mapped[
        ChatChannelStatus
    ] = mapped_column(
        Enum(ChatChannelStatus),
        default=ChatChannelStatus.ACTIVE,
        server_default=ChatChannelStatus.ACTIVE.value,
        nullable=False,
        index=True,
    )

    configuration: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    knowledge_base: Mapped[
        "KnowledgeBase"
    ] = relationship(
        "KnowledgeBase",
    )

    tenant: Mapped[
        "Tenant"
    ] = relationship(
        "Tenant",
    )

    api_keys: Mapped[
        list["ChatChannelApiKey"]
    ] = relationship(
        "ChatChannelApiKey",
        back_populates="channel",
        cascade="all, delete-orphan",
    )

    conversations: Mapped[
        list["Conversation"]
    ] = relationship(
        "Conversation",
        back_populates="chat_channel",
        cascade="all, delete-orphan",
    )