from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.usage_limit import (
    UsageLimit,
)
from app.repositories.base_repository import (
    BaseRepository,
)


class UsageLimitRepository(
    BaseRepository[
        UsageLimit
    ],
):

    def __init__(self):
        super().__init__(
            UsageLimit,
        )

    def get_tenant_limit(
        self,
        db: Session,
        tenant_id: UUID,
    ) -> UsageLimit | None:
        stmt = (
            select(
                UsageLimit
            )
            .where(
                UsageLimit.tenant_id
                == tenant_id,

                UsageLimit
                .knowledge_base_id
                .is_(None),

                UsageLimit
                .chat_channel_id
                .is_(None),
            )
        )

        return (
            db.execute(
                stmt
            )
            .scalars()
            .first()
        )

    def get_knowledge_base_limit(
        self,
        db: Session,
        knowledge_base_id: UUID,
    ) -> UsageLimit | None:
        stmt = (
            select(
                UsageLimit
            )
            .where(
                UsageLimit
                .knowledge_base_id
                == knowledge_base_id,

                UsageLimit
                .chat_channel_id
                .is_(None),
            )
        )

        return (
            db.execute(
                stmt
            )
            .scalars()
            .first()
        )

    def get_chat_channel_limit(
        self,
        db: Session,
        chat_channel_id: UUID,
    ) -> UsageLimit | None:
        stmt = (
            select(
                UsageLimit
            )
            .where(
                UsageLimit
                .chat_channel_id
                == chat_channel_id,
            )
        )

        return (
            db.execute(
                stmt
            )
            .scalars()
            .first()
        )