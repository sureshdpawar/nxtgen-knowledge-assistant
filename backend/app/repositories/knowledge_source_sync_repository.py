from uuid import UUID

from sqlalchemy import (
    select,
)
from sqlalchemy.orm import Session

from app.core.enums import (
    KnowledgeSourceSyncStatus,
)
from app.models.knowledge_source_sync import (
    KnowledgeSourceSync,
)
from app.repositories.base_repository import (
    BaseRepository,
)


class KnowledgeSourceSyncRepository(
    BaseRepository[
        KnowledgeSourceSync
    ]
):

    def __init__(self):
        super().__init__(
            KnowledgeSourceSync
        )

    def list_by_source(
        self,
        db: Session,
        knowledge_source_id: UUID,
    ) -> list[
        KnowledgeSourceSync
    ]:

        stmt = (
            select(
                KnowledgeSourceSync
            )
            .where(
                KnowledgeSourceSync
                .knowledge_source_id
                == knowledge_source_id
            )
            .order_by(
                KnowledgeSourceSync
                .created_at
                .desc()
            )
        )

        return (
            db.execute(stmt)
            .scalars()
            .all()
        )

    def get_active_for_source(
        self,
        db: Session,
        knowledge_source_id: UUID,
    ) -> (
        KnowledgeSourceSync
        | None
    ):

        stmt = (
            select(
                KnowledgeSourceSync
            )
            .where(
                KnowledgeSourceSync
                .knowledge_source_id
                == knowledge_source_id,

                KnowledgeSourceSync
                .status
                .in_(
                    [
                        KnowledgeSourceSyncStatus.PENDING,
                        KnowledgeSourceSyncStatus.RUNNING,
                    ]
                ),
            )
            .order_by(
                KnowledgeSourceSync
                .created_at
                .desc()
            )
        )

        return (
            db.execute(stmt)
            .scalars()
            .first()
        )