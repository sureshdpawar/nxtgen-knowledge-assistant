from uuid import UUID

from sqlalchemy import (
    delete,
    select,
)
from sqlalchemy.orm import Session

from app.models.knowledge_base import (
    KnowledgeBase,
)
from app.models.user_knowledge_base_access import (
    UserKnowledgeBaseAccess,
)
from app.repositories.base_repository import (
    BaseRepository,
)


class UserKnowledgeBaseAccessRepository(
    BaseRepository[
        UserKnowledgeBaseAccess
    ],
):

    def __init__(self):
        super().__init__(
            UserKnowledgeBaseAccess
        )

    def list_for_user(
        self,
        db: Session,
        user_id: UUID,
    ):
        stmt = (
            select(
                KnowledgeBase,
            )
            .join(
                UserKnowledgeBaseAccess,
                UserKnowledgeBaseAccess
                .knowledge_base_id
                == KnowledgeBase.id,
            )
            .where(
                UserKnowledgeBaseAccess.user_id
                == user_id,
            )
            .order_by(
                KnowledgeBase.name,
            )
        )

        return list(
            db.scalars(stmt).all()
        )

    def get_assignment(
        self,
        db: Session,
        user_id: UUID,
        knowledge_base_id: UUID,
    ):
        stmt = (
            select(
                UserKnowledgeBaseAccess
            )
            .where(
                UserKnowledgeBaseAccess.user_id
                == user_id,
                UserKnowledgeBaseAccess
                .knowledge_base_id
                == knowledge_base_id,
            )
        )

        return db.scalar(stmt)

    def delete_assignment(
        self,
        db: Session,
        user_id: UUID,
        knowledge_base_id: UUID,
    ):
        stmt = (
            delete(
                UserKnowledgeBaseAccess
            )
            .where(
                UserKnowledgeBaseAccess.user_id
                == user_id,
                UserKnowledgeBaseAccess
                .knowledge_base_id
                == knowledge_base_id,
            )
        )

        db.execute(stmt)