from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
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
    from app.models.chat_channel import ChatChannel
    from app.models.conversation_message import ConversationMessage
    from app.models.knowledge_base import KnowledgeBase
    from app.models.tenant import Tenant
    from app.models.user import User


class Conversation(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "conversation"

    __table_args__ = (
        CheckConstraint(
            """
            (
                user_id IS NOT NULL
                AND chat_channel_id IS NULL
            )
            OR
            (
                user_id IS NULL
                AND chat_channel_id IS NOT NULL
            )
            """,
            name="ck_conversation_single_actor",
        ),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenant.id"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[
        UUID | None
    ] = mapped_column(
        ForeignKey("app_user.id"),
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

    knowledge_base_id: Mapped[UUID] = mapped_column(
        ForeignKey("knowledge_base.id"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    tenant: Mapped[
        "Tenant"
    ] = relationship(
        "Tenant",
        back_populates="conversations",
    )

    user: Mapped[
        "User | None"
    ] = relationship(
        "User",
        back_populates="conversations",
    )

    chat_channel: Mapped[
        "ChatChannel | None"
    ] = relationship(
        "ChatChannel",
        back_populates="conversations",
    )

    knowledge_base: Mapped[
        "KnowledgeBase"
    ] = relationship(
        "KnowledgeBase",
    )

    messages: Mapped[
        list["ConversationMessage"]
    ] = relationship(
        "ConversationMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ConversationMessage.created_at",
    )