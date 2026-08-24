from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
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

    def _validate_chunking_config(
        self,
        chunk_size: int | None,
        chunk_overlap: int | None,
    ) -> None:
        """
        Validate the effective chunking
        configuration.

        A None value means the knowledge
        base inherits the corresponding
        platform default.
        """

        effective_chunk_size = (
            chunk_size
            if chunk_size is not None
            else settings.CHUNK_SIZE
        )

        effective_chunk_overlap = (
            chunk_overlap
            if chunk_overlap is not None
            else settings.CHUNK_OVERLAP
        )

        if (
            effective_chunk_overlap
            >= effective_chunk_size
        ):
            raise ValueError(
                "chunk_overlap must be "
                "less than chunk_size."
            )

    def create(
        self,
        db: Session,
        current_user: User,
        payload: KnowledgeBaseCreate,
    ) -> KnowledgeBase:

        self._validate_chunking_config(
            chunk_size=
                payload.chunk_size,
            chunk_overlap=
                payload.chunk_overlap,
        )

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

                chunk_size=
                    payload.chunk_size,

                chunk_overlap=
                    payload.chunk_overlap,

                top_k=
                    payload.top_k,
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

        #
        # Work out what the resulting
        # chunk configuration will be
        # before modifying the model.
        #
        # An omitted field preserves the
        # existing KB override.
        #
        # An explicitly supplied None
        # removes the override and causes
        # the platform default to apply.
        #
        resulting_chunk_size = (
            updates["chunk_size"]
            if "chunk_size" in updates
            else knowledge_base.chunk_size
        )

        resulting_chunk_overlap = (
            updates["chunk_overlap"]
            if "chunk_overlap" in updates
            else knowledge_base.chunk_overlap
        )

        self._validate_chunking_config(
            chunk_size=
                resulting_chunk_size,
            chunk_overlap=
                resulting_chunk_overlap,
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