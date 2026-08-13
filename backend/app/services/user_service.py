# app/services/user_service.py

from uuid import UUID

from sqlalchemy.orm import Session

from app.auth.password import (
    hash_password,
)
from app.core.enums import UserRole
from app.exceptions.tenant import (
    TenantNotFoundError,
)
from app.exceptions.user import (
    DuplicateUserEmailError,
    UserNotFoundError,
)
from app.models.user import User
from app.repositories.tenant_repository import (
    TenantRepository,
)
from app.repositories.user_repository import (
    UserRepository,
)
from app.schemas.user import (
    TenantAdminCreate,
    TenantAdminUpdate,
    UserCreate,
    UserUpdate,
)


class UserService:

    def __init__(self):
        self.user_repository = (
            UserRepository()
        )

        self.tenant_repository = (
            TenantRepository()
        )

    def create(
        self,
        db: Session,
        current_user: User,
        user_create: UserCreate,
    ) -> User:

        if current_user.tenant_id is None:
            raise UserNotFoundError()

        existing_user = (
            self.user_repository
            .get_by_email(
                db,
                user_create.email,
            )
        )

        if existing_user:
            raise DuplicateUserEmailError()

        user = User(
            tenant_id=
                current_user.tenant_id,
            first_name=
                user_create.first_name,
            last_name=
                user_create.last_name,
            email=
                user_create.email,
            password_hash=
                hash_password(
                    user_create.password,
                ),
            role=
                UserRole.USER,
            is_active=True,
        )

        self.user_repository.create(
            db,
            user,
        )

        db.commit()
        db.refresh(user)

        return user

    def create_tenant_admin(
        self,
        db: Session,
        tenant_id: UUID,
        admin_create:
            TenantAdminCreate,
    ) -> User:

        tenant = (
            self.tenant_repository
            .get(
                db,
                tenant_id,
            )
        )

        if tenant is None:
            raise TenantNotFoundError()

        existing_user = (
            self.user_repository
            .get_by_email(
                db,
                admin_create.email,
            )
        )

        if existing_user:
            raise DuplicateUserEmailError()

        user = User(
            tenant_id=tenant_id,
            first_name=
                admin_create.first_name,
            last_name=
                admin_create.last_name,
            email=
                admin_create.email,
            password_hash=
                hash_password(
                    admin_create.password,
                ),
            role=
                UserRole.ADMIN,
            is_active=True,
        )

        self.user_repository.create(
            db,
            user,
        )

        db.commit()
        db.refresh(user)

        return user

    def list_tenant_admins(
        self,
        db: Session,
        tenant_id: UUID,
    ) -> list[User]:

        tenant = (
            self.tenant_repository
            .get(
                db,
                tenant_id,
            )
        )

        if tenant is None:
            raise TenantNotFoundError()

        return (
            self.user_repository
            .list_admins_by_tenant(
                db=db,
                tenant_id=
                    tenant_id,
            )
        )

    def get_tenant_admin(
        self,
        db: Session,
        tenant_id: UUID,
        user_id: UUID,
    ) -> User:

        tenant = (
            self.tenant_repository
            .get(
                db,
                tenant_id,
            )
        )

        if tenant is None:
            raise TenantNotFoundError()

        user = (
            self.user_repository
            .get(
                db,
                user_id,
            )
        )

        if (
            user is None
            or user.tenant_id
            != tenant_id
            or user.role
            != UserRole.ADMIN
        ):
            raise UserNotFoundError()

        return user

    def update_tenant_admin(
        self,
        db: Session,
        tenant_id: UUID,
        user_id: UUID,
        admin_update:
            TenantAdminUpdate,
    ) -> User:

        user = (
            self.get_tenant_admin(
                db=db,
                tenant_id=
                    tenant_id,
                user_id=user_id,
            )
        )

        update_data = (
            admin_update.model_dump(
                exclude_unset=True,
            )
        )

        for (
            field,
            value,
        ) in update_data.items():
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
        db.refresh(user)

        return user

    def get(
        self,
        db: Session,
        current_user: User,
        user_id: UUID,
    ) -> User:

        user = (
            self.user_repository
            .get(
                db,
                user_id,
            )
        )

        if user is None:
            raise UserNotFoundError()

        if (
            current_user.tenant_id
            is None
            or user.tenant_id
            != current_user.tenant_id
        ):
            raise UserNotFoundError()

        return user

    def list(
        self,
        db: Session,
        current_user: User,
    ) -> list[User]:

        if current_user.tenant_id is None:
            return []

        return (
            self.user_repository
            .list_by_tenant(
                db,
                current_user.tenant_id,
            )
        )

    def update(
        self,
        db: Session,
        current_user: User,
        user_id: UUID,
        user_update:
            UserUpdate,
    ) -> User:

        user = self.get(
            db=db,
            current_user=
                current_user,
            user_id=user_id,
        )

        update_data = (
            user_update.model_dump(
                exclude_unset=True,
            )
        )

        for (
            field,
            value,
        ) in update_data.items():
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
        db.refresh(user)

        return user

    def delete(
        self,
        db: Session,
        current_user: User,
        user_id: UUID,
    ) -> None:

        user = self.get(
            db=db,
            current_user=
                current_user,
            user_id=user_id,
        )

        self.user_repository.delete(
            db,
            user,
        )

        db.commit()