from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.models.user import User
from app.repositories.base_repository import (
    BaseRepository,
)


class UserRepository(
    BaseRepository[User],
):

    def __init__(self):
        super().__init__(User)

    def get_by_email(
        self,
        db: Session,
        email: str,
    ) -> User | None:

        stmt = (
            select(User)
            .where(
                User.email == email,
            )
        )

        return (
            db.execute(stmt)
            .scalar_one_or_none()
        )

    def list_by_tenant(
        self,
        db: Session,
        tenant_id: UUID,
    ) -> list[User]:

        stmt = (
            select(User)
            .where(
                User.tenant_id
                == tenant_id,
            )
            .order_by(
                User.first_name,
                User.last_name,
            )
        )

        return list(
            db.scalars(stmt).all()
        )

    def list_admins_by_tenant(
        self,
        db: Session,
        tenant_id: UUID,
    ) -> list[User]:

        stmt = (
            select(User)
            .where(
                User.tenant_id
                == tenant_id,
                User.role
                == UserRole.ADMIN,
            )
            .order_by(
                User.first_name,
                User.last_name,
            )
        )

        return list(
            db.scalars(stmt).all()
        )