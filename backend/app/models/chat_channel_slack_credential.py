from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
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


class ChatChannelSlackCredential(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = (
        "chat_channel_slack_credential"
    )

    channel_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "chat_channel.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    slack_team_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
    )

    slack_team_name: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True,
    )

    bot_user_id: Mapped[
        str | None
    ] = mapped_column(
        String(64),
        nullable=True,
    )

    bot_token: Mapped[str] = mapped_column(
        String(2048),
        nullable=False,
    )

    signing_secret: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )

    channel: Mapped[
        "ChatChannel"
    ] = relationship(
        "ChatChannel",
        back_populates=(
            "slack_credential"
        ),
    )