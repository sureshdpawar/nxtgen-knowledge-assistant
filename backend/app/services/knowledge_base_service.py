from uuid import UUID

from sqlalchemy.orm import Session

from app.exceptions.knowledge_base import (
    KnowledgeBaseNotFoundError,
)
from app.models.knowledge_base import (
    KnowledgeBase,
)
from app.models.user import User
from app.repositories.knowledge_base_repository import (
    KnowledgeBaseRepository,
)
from app.schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
)


class KnowledgeBaseService:

    def __init__(self):
        self.repository = (
            KnowledgeBaseRepository()
        )

    def create(
        self,
        db: Session,
        current_user: User,
        payload: KnowledgeBaseCreate,
    ) -> KnowledgeBase:

        knowledge_base = (
            KnowledgeBase(
                tenant_id=
                    current_user.tenant_id,

                owner_user_id=
                    current_user.id,

                name=
                    payload.name,

                description=
                    payload.description,

                visibility=
                    payload.visibility,
            )
        )

        knowledge_base = (
            self.repository.create(
                db,
                knowledge_base,
            )
        )

        db.commit()
        db.refresh(
            knowledge_base,
        )

        return knowledge_base

    def list(
        self,
        db: Session,
        current_user: User,
    ) -> list[KnowledgeBase]:

        return (
            self.repository.filter_by(
                db,
                tenant_id=
                    current_user.tenant_id,
            )
        )

    def get(
        self,
        db: Session,
        current_user: User,
        knowledge_base_id: UUID,
    ) -> KnowledgeBase:

        knowledge_base = (
            self.repository.get(
                db,
                knowledge_base_id,
            )
        )

        if (
            knowledge_base is None
            or
            knowledge_base.tenant_id
            != current_user.tenant_id
        ):
            raise (
                KnowledgeBaseNotFoundError()
            )

        return knowledge_base

    def update(
        self,
        db: Session,
        current_user: User,
        knowledge_base_id: UUID,
        payload: KnowledgeBaseUpdate,
    ) -> KnowledgeBase:

        knowledge_base = (
            self.get(
                db,
                current_user,
                knowledge_base_id,
            )
        )

        updates = (
            payload.model_dump(
                exclude_unset=True,
            )
        )

        for (
            field,
            value,
        ) in updates.items():

            setattr(
                knowledge_base,
                field,
                value,
            )

        knowledge_base = (
            self.repository.update(
                db,
                knowledge_base,
            )
        )

        db.commit()
        db.refresh(
            knowledge_base,
        )

        return knowledge_base

    def delete(
        self,
        db: Session,
        current_user: User,
        knowledge_base_id: UUID,
    ) -> None:

        knowledge_base = (
            self.get(
                db,
                current_user,
                knowledge_base_id,
            )
        )

        self.repository.delete(
            db,
            knowledge_base,
        )

        db.commit()