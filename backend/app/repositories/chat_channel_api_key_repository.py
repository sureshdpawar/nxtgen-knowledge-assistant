from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chat_channel_api_key import (
    ChatChannelApiKey,
)
from app.repositories.base_repository import (
    BaseRepository,
)


class ChatChannelApiKeyRepository(
    BaseRepository[
        ChatChannelApiKey
    ]
):
    def __init__(self):
        super().__init__(
            ChatChannelApiKey
        )

    def list_by_channel(
        self,
        db: Session,
        channel_id: UUID,
    ) -> list[
        ChatChannelApiKey
    ]:
        stmt = (
            select(
                ChatChannelApiKey
            )
            .where(
                ChatChannelApiKey.channel_id
                == channel_id
            )
            .order_by(
                ChatChannelApiKey
                .created_at
                .desc()
            )
        )

        return list(
            db.scalars(stmt).all()
        )

    def get_by_hash(
        self,
        db: Session,
        key_hash: str,
    ) -> ChatChannelApiKey | None:
        stmt = (
            select(
                ChatChannelApiKey
            )
            .where(
                ChatChannelApiKey.key_hash
                == key_hash
            )
        )

        return (
            db.execute(stmt)
            .scalars()
            .first()
        )

    def get_for_channel(
        self,
        db: Session,
        key_id: UUID,
        channel_id: UUID,
    ) -> ChatChannelApiKey | None:
        stmt = (
            select(
                ChatChannelApiKey
            )
            .where(
                ChatChannelApiKey.id
                == key_id,
                ChatChannelApiKey.channel_id
                == channel_id,
            )
        )

        return (
            db.execute(stmt)
            .scalars()
            .first()
        )