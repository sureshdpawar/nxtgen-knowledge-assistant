from uuid import UUID

from sqlalchemy.orm import Session

from app.exceptions.knowledge_base import KnowledgeBaseNotFoundError
from app.exceptions.knowledge_source import (
    KnowledgeSourceNotFoundError,
)
from app.models.knowledge_source import KnowledgeSource
from app.models.user import User
from app.repositories.knowledge_base_repository import (
    KnowledgeBaseRepository,
)
from app.repositories.knowledge_source_repository import (
    KnowledgeSourceRepository,
)
from app.schemas.knowledge_source import (
    KnowledgeSourceCreate,
    KnowledgeSourceUpdate,
)


class KnowledgeSourceService:

    def __init__(self):
        self.repository = KnowledgeSourceRepository()
        self.kb_repository = KnowledgeBaseRepository()

    def create(
        self,
        db: Session,
        current_user: User,
        knowledge_base_id: UUID,
        payload: KnowledgeSourceCreate,
    ) -> KnowledgeSource:

        knowledge_base = self.kb_repository.get(
            db,
            knowledge_base_id,
        )

        if (
            knowledge_base is None
            or knowledge_base.tenant_id != current_user.tenant_id
        ):
            raise KnowledgeBaseNotFoundError()

        knowledge_source = KnowledgeSource(
            knowledge_base_id=knowledge_base.id,
            created_by=current_user.id,
            name=payload.name,
            type=payload.type,
            configuration=payload.configuration,
        )

        return self.repository.create(
            db,
            knowledge_source,
        )

    def list(
        self,
        db: Session,
        current_user: User,
        knowledge_base_id: UUID,
    ) -> list[KnowledgeSource]:

        knowledge_base = self.kb_repository.get(
            db,
            knowledge_base_id,
        )

        if (
            knowledge_base is None
            or knowledge_base.tenant_id != current_user.tenant_id
        ):
            raise KnowledgeBaseNotFoundError()

        return self.repository.filter_by(
            db,
            knowledge_base_id=knowledge_base_id,
        )

    def get(
        self,
        db: Session,
        current_user: User,
        knowledge_source_id: UUID,
    ) -> KnowledgeSource:

        knowledge_source = self.repository.get(
            db,
            knowledge_source_id,
        )

        if knowledge_source is None:
            raise KnowledgeSourceNotFoundError()

        if (
            knowledge_source.knowledge_base.tenant_id
            != current_user.tenant_id
        ):
            raise KnowledgeSourceNotFoundError()

        return knowledge_source

    def update(
        self,
        db: Session,
        current_user: User,
        knowledge_source_id: UUID,
        payload: KnowledgeSourceUpdate,
    ) -> KnowledgeSource:

        knowledge_source = self.get(
            db,
            current_user,
            knowledge_source_id,
        )

        for field, value in payload.model_dump(
            exclude_unset=True,
        ).items():
            setattr(
                knowledge_source,
                field,
                value,
            )

        return self.repository.update(
            db,
            knowledge_source,
        )

    def delete(
        self,
        db: Session,
        current_user: User,
        knowledge_source_id: UUID,
    ) -> None:

        knowledge_source = self.get(
            db,
            current_user,
            knowledge_source_id,
        )

        self.repository.delete(
            db,
            knowledge_source,
        )