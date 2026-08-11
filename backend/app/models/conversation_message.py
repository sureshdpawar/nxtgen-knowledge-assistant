from uuid import UUID

from sqlalchemy import (
    ForeignKey,
    JSON,
    String,
    Text,
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


class ConversationMessage(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "conversation_message"

    conversation_id: Mapped[UUID] = mapped_column(
        ForeignKey("conversation.id"),
        nullable=False,
        index=True,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    citations: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    token_usage: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    conversation: Mapped["Conversation"] = relationship(
        "Conversation",
        back_populates="messages",
    )