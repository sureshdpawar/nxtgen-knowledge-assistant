from uuid import UUID

from sqlalchemy.orm import Session

from app.auth.password import hash_password
from app.exceptions.tenant import TenantNotFoundError
from app.exceptions.user import (
    DuplicateUserEmailError,
    UserNotFoundError,
)
from app.models.user import User
from app.repositories.tenant_repository import TenantRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:

    def __init__(self):
        self.user_repository = UserRepository()
        self.tenant_repository = TenantRepository()

    def create(
        self,
        db: Session,
        user_create: UserCreate,
    ) -> User:

        tenant = self.tenant_repository.get(
            db,
            user_create.tenant_id,
        )

        if tenant is None:
            raise TenantNotFoundError()

        existing_user = self.user_repository.get_by_email(
            db,
            user_create.email,
        )

        if existing_user:
            raise DuplicateUserEmailError()

        user = User(
            tenant_id=user_create.tenant_id,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            email=user_create.email,
            password_hash=hash_password(user_create.password),
            role=user_create.role,
            is_active=True,
        )

        self.user_repository.create(
            db,
            user,
        )

        db.commit()

        return user

    def get(
        self,
        db: Session,
        user_id: UUID,
    ) -> User:

        user = self.user_repository.get(
            db,
            user_id,
        )

        if user is None:
            raise UserNotFoundError()

        return user

    def list(
        self,
        db: Session,
    ) -> list[User]:

        return self.user_repository.list(db)

    def update(
        self,
        db: Session,
        user_id: UUID,
        user_update: UserUpdate,
    ) -> User:

        user = self.get(
            db,
            user_id,
        )

        update_data = user_update.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(
                user,
                field,
                value,
            )

        self.user_repository.update(
            db,
            user,
        )

        db.commit()

        return user

    def delete(
        self,
        db: Session,
        user_id: UUID,
    ) -> None:

        user = self.get(
            db,
            user_id,
        )

        self.user_repository.delete(
            db,
            user,
        )

        db.commit()