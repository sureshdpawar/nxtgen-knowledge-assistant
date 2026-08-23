from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chat_channel import ChatChannel
from app.repositories.base_repository import BaseRepository


class ChatChannelRepository(
    BaseRepository[ChatChannel]
):
    def __init__(self):
        super().__init__(
            ChatChannel
        )

    def list_by_tenant(
        self,
        db: Session,
        tenant_id: UUID,
    ) -> list[ChatChannel]:
        stmt = (
            select(ChatChannel)
            .where(
                ChatChannel.tenant_id
                == tenant_id
            )
            .order_by(
                ChatChannel.created_at.desc()
            )
        )

        return list(
            db.scalars(stmt).all()
        )

    def list_by_knowledge_base(
        self,
        db: Session,
        knowledge_base_id: UUID,
    ) -> list[ChatChannel]:
        stmt = (
            select(ChatChannel)
            .where(
                ChatChannel.knowledge_base_id
                == knowledge_base_id
            )
            .order_by(
                ChatChannel.created_at.desc()
            )
        )

        return list(
            db.scalars(stmt).all()
        )

    def get_for_tenant(
        self,
        db: Session,
        channel_id: UUID,
        tenant_id: UUID,
    ) -> ChatChannel | None:
        stmt = (
            select(ChatChannel)
            .where(
                ChatChannel.id
                == channel_id,
                ChatChannel.tenant_id
                == tenant_id,
            )
        )

        return (
            db.execute(stmt)
            .scalars()
            .first()
        )