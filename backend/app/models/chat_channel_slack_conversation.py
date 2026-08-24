from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
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


class ChatChannelSlackConversation(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = (
        "chat_channel_slack_conversation"
    )

    __table_args__ = (
        UniqueConstraint(
            "conversation_id",
        ),
        UniqueConstraint(
            "channel_id",
            "slack_team_id",
            "slack_channel_id",
            "slack_thread_ts",
            name=(
                "uq_slack_conversation_thread"
            ),
        ),
        Index(
            "ix_chat_channel_slack_conversation_conversation_id",
            "conversation_id",
            unique=True,
        ),
    )

    channel_id: Mapped[
        UUID
    ] = mapped_column(
        ForeignKey(
            "chat_channel.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    conversation_id: Mapped[
        UUID
    ] = mapped_column(
        ForeignKey(
            "conversation.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    slack_team_id: Mapped[
        str
    ] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    slack_channel_id: Mapped[
        str
    ] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    slack_thread_ts: Mapped[
        str
    ] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    slack_user_id: Mapped[
        str | None
    ] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    channel: Mapped[
        "ChatChannel"
    ] = relationship(
        "ChatChannel",
    )

    conversation: Mapped[
        "Conversation"
    ] = relationship(
        "Conversation",
    )