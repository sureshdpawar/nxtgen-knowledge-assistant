from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):

    def __init__(self):
        super().__init__(User)

    def get_by_email(
        self,
        db: Session,
        email: str,
    ) -> User | None:

        stmt = select(User).where(
            User.email == email,
        )

        return db.execute(stmt).scalar_one_or_none()

    def list_by_tenant(
        self,
        db: Session,
        tenant_id: UUID,
    ) -> list[User]:

        stmt = select(User).where(
            User.tenant_id == tenant_id,
        )

        return db.execute(stmt).scalars().all()