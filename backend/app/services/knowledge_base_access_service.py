from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import (
    KnowledgeBaseAccessLevel,
    UserRole,
)
from app.exceptions.knowledge_base_access import (
    CrossTenantKnowledgeBaseAccessError,
    KnowledgeBaseAccessDeniedError,
    KnowledgeBaseAccessKnowledgeBaseNotFoundError,
    KnowledgeBaseAccessUserNotFoundError,
)
from app.models.knowledge_base import (
    KnowledgeBase,
)
from app.models.user import User
from app.models.user_knowledge_base_access import (
    UserKnowledgeBaseAccess,
)
from app.repositories.user_knowledge_base_access_repository import (
    UserKnowledgeBaseAccessRepository,
)


class KnowledgeBaseAccessService:

    def __init__(self):
        self.repository = (
            UserKnowledgeBaseAccessRepository()
        )

    def list_accessible(
        self,
        db: Session,
        current_user: User,
    ) -> list[KnowledgeBase]:

        if (
            current_user.role
            == UserRole.ADMIN
        ):
            stmt = (
                select(
                    KnowledgeBase,
                )
                .where(
                    KnowledgeBase.tenant_id
                    == current_user.tenant_id,
                )
                .order_by(
                    KnowledgeBase.name,
                )
            )

            return list(
                db.scalars(stmt).all()
            )

        if (
            current_user.role
            == UserRole.USER
        ):
            return (
                self.repository.list_for_user(
                    db=db,
                    user_id=current_user.id,
                )
            )

        if (
            current_user.role
            == UserRole.SUPERADMIN
        ):
            return []

        raise (
            KnowledgeBaseAccessDeniedError(
                "You do not have access "
                "to knowledge bases."
            )
        )

    def list_for_user(
        self,
        db: Session,
        current_user: User,
        user_id: UUID,
    ) -> list[KnowledgeBase]:

        self._require_admin(
            current_user,
        )

        user = db.get(
            User,
            user_id,
        )

        if user is None:
            raise (
                KnowledgeBaseAccessUserNotFoundError()
            )

        if (
            user.tenant_id
            != current_user.tenant_id
        ):
            raise (
                CrossTenantKnowledgeBaseAccessError()
            )

        if (
            user.role
            != UserRole.USER
        ):
            raise (
                KnowledgeBaseAccessDeniedError(
                    "Knowledge base access "
                    "can only be viewed "
                    "for USER accounts."
                )
            )

        return (
            self.repository.list_for_user(
                db=db,
                user_id=user_id,
            )
        )

    def assign(
        self,
        db: Session,
        current_user: User,
        user_id: UUID,
        knowledge_base_id: UUID,
        access_level:
            KnowledgeBaseAccessLevel,
    ) -> UserKnowledgeBaseAccess:

        self._require_admin(
            current_user,
        )

        user = db.get(
            User,
            user_id,
        )

        if user is None:
            raise (
                KnowledgeBaseAccessUserNotFoundError()
            )

        knowledge_base = db.get(
            KnowledgeBase,
            knowledge_base_id,
        )

        if knowledge_base is None:
            raise (
                KnowledgeBaseAccessKnowledgeBaseNotFoundError()
            )

        self._validate_same_tenant(
            current_user=current_user,
            user=user,
            knowledge_base=knowledge_base,
        )

        if (
            user.role
            != UserRole.USER
        ):
            raise (
                KnowledgeBaseAccessDeniedError(
                    "Knowledge base access "
                    "can only be assigned "
                    "to USER accounts."
                )
            )

        existing = (
            self.repository.get_assignment(
                db=db,
                user_id=user_id,
                knowledge_base_id=
                    knowledge_base_id,
            )
        )

        if existing is not None:
            existing.access_level = (
                access_level
            )

            db.commit()
            db.refresh(existing)

            return existing

        assignment = (
            UserKnowledgeBaseAccess(
                user_id=user_id,
                knowledge_base_id=
                    knowledge_base_id,
                access_level=
                    access_level,
            )
        )

        db.add(assignment)
        db.commit()
        db.refresh(assignment)

        return assignment

    def revoke(
        self,
        db: Session,
        current_user: User,
        user_id: UUID,
        knowledge_base_id: UUID,
    ) -> None:

        self._require_admin(
            current_user,
        )

        user = db.get(
            User,
            user_id,
        )

        if user is None:
            raise (
                KnowledgeBaseAccessUserNotFoundError()
            )

        knowledge_base = db.get(
            KnowledgeBase,
            knowledge_base_id,
        )

        if knowledge_base is None:
            raise (
                KnowledgeBaseAccessKnowledgeBaseNotFoundError()
            )

        self._validate_same_tenant(
            current_user=current_user,
            user=user,
            knowledge_base=knowledge_base,
        )

        self.repository.delete_assignment(
            db=db,
            user_id=user_id,
            knowledge_base_id=
                knowledge_base_id,
        )

        db.commit()

    def has_access(
        self,
        db: Session,
        current_user: User,
        knowledge_base_id: UUID,
    ) -> bool:

        knowledge_base = db.get(
            KnowledgeBase,
            knowledge_base_id,
        )

        if knowledge_base is None:
            return False

        if (
            current_user.role
            == UserRole.ADMIN
        ):
            return (
                knowledge_base.tenant_id
                == current_user.tenant_id
            )

        if (
            current_user.role
            == UserRole.USER
        ):
            if (
                knowledge_base.tenant_id
                != current_user.tenant_id
            ):
                return False

            assignment = (
                self.repository.get_assignment(
                    db=db,
                    user_id=current_user.id,
                    knowledge_base_id=
                        knowledge_base_id,
                )
            )

            return (
                assignment is not None
            )

        if (
            current_user.role
            == UserRole.SUPERADMIN
        ):
            return False

        return False

    def require_access(
        self,
        db: Session,
        current_user: User,
        knowledge_base_id: UUID,
    ) -> None:

        if not self.has_access(
            db=db,
            current_user=current_user,
            knowledge_base_id=
                knowledge_base_id,
        ):
            raise (
                KnowledgeBaseAccessDeniedError(
                    "You do not have access "
                    "to this knowledge base."
                )
            )

    def _require_admin(
        self,
        current_user: User,
    ) -> None:

        if (
            current_user.role
            != UserRole.ADMIN
        ):
            raise (
                KnowledgeBaseAccessDeniedError()
            )

    def _validate_same_tenant(
        self,
        current_user: User,
        user: User,
        knowledge_base:
            KnowledgeBase,
    ) -> None:

        if (
            user.tenant_id
            != current_user.tenant_id
        ):
            raise (
                CrossTenantKnowledgeBaseAccessError()
            )

        if (
            knowledge_base.tenant_id
            != current_user.tenant_id
        ):
            raise (
                CrossTenantKnowledgeBaseAccessError()
            )