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
        required_level:
            KnowledgeBaseAccessLevel =
            KnowledgeBaseAccessLevel.READ,
    ) -> bool:
        """
        Determine whether the authenticated user
        has the requested level of access to a
        Knowledge Base.

        Rules:

        ADMIN
        -----
        ADMIN users implicitly have MANAGE access
        to all Knowledge Bases within their own
        tenant.

        USER
        ----
        USER access comes from the explicit
        UserKnowledgeBaseAccess assignment.

        READ assignment:
            - satisfies READ
            - does NOT satisfy MANAGE

        MANAGE assignment:
            - satisfies READ
            - satisfies MANAGE

        SUPERADMIN
        ----------
        SUPERADMIN does not implicitly participate
        in tenant Knowledge Base access.
        """

        knowledge_base = db.get(
            KnowledgeBase,
            knowledge_base_id,
        )

        if knowledge_base is None:
            return False

        #
        # ADMIN:
        #
        # Full KB management rights inside
        # the user's own tenant only.
        #
        if (
            current_user.role
            == UserRole.ADMIN
        ):
            return (
                knowledge_base.tenant_id
                == current_user.tenant_id
            )

        #
        # USER:
        #
        # Must belong to the same tenant and
        # have an explicit KB assignment.
        #
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

            if assignment is None:
                return False

            return (
                self._access_level_satisfies(
                    actual_level=
                        assignment.access_level,
                    required_level=
                        required_level,
                )
            )

        #
        # SUPERADMIN:
        #
        # Platform administration should not
        # automatically expose tenant KB data.
        #
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
        required_level:
            KnowledgeBaseAccessLevel =
            KnowledgeBaseAccessLevel.READ,
    ) -> None:
        """
        Raise when the user does not have the
        required Knowledge Base access level.

        Default remains READ so existing callers
        continue to work without modification.
        """

        if not self.has_access(
            db=db,
            current_user=current_user,
            knowledge_base_id=
                knowledge_base_id,
            required_level=
                required_level,
        ):
            raise (
                KnowledgeBaseAccessDeniedError(
                    "You do not have "
                    f"{required_level.value} "
                    "access to this "
                    "knowledge base."
                )
            )

    def require_read_access(
        self,
        db: Session,
        current_user: User,
        knowledge_base_id: UUID,
    ) -> None:
        """
        Convenience helper for read-only
        operations.
        """

        self.require_access(
            db=db,
            current_user=current_user,
            knowledge_base_id=
                knowledge_base_id,
            required_level=
                KnowledgeBaseAccessLevel.READ,
        )

    def require_manage_access(
        self,
        db: Session,
        current_user: User,
        knowledge_base_id: UUID,
    ) -> None:
        """
        Convenience helper for operations that
        modify Knowledge Base content or
        configuration.
        """

        self.require_access(
            db=db,
            current_user=current_user,
            knowledge_base_id=
                knowledge_base_id,
            required_level=
                KnowledgeBaseAccessLevel.MANAGE,
        )

    def _access_level_satisfies(
        self,
        actual_level:
            KnowledgeBaseAccessLevel,
        required_level:
            KnowledgeBaseAccessLevel,
    ) -> bool:
        """
        Access hierarchy:

            MANAGE >= READ
            READ   >= READ

        There are currently only two access
        levels, so keeping the hierarchy explicit
        is safer than relying on enum ordering.
        """

        if (
            required_level
            == KnowledgeBaseAccessLevel.READ
        ):
            return (
                actual_level
                in {
                    KnowledgeBaseAccessLevel.READ,
                    KnowledgeBaseAccessLevel.MANAGE,
                }
            )

        if (
            required_level
            == KnowledgeBaseAccessLevel.MANAGE
        ):
            return (
                actual_level
                == KnowledgeBaseAccessLevel.MANAGE
            )

        return False

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