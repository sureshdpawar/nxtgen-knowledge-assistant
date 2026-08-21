from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
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
    from app.models.chat_channel import (
        ChatChannel,
    )


class ChatChannelApiKey(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "chat_channel_api_key"

    channel_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "chat_channel.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    key_prefix: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
    )

    key_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    last_used_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    channel: Mapped[
        "ChatChannel"
    ] = relationship(
        "ChatChannel",
        back_populates="api_keys",
    )