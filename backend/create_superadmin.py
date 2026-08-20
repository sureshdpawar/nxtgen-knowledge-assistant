import getpass

from app.auth.password import hash_password
from app.core.enums import UserRole
from app.db.session import SessionLocal
from app.models.user import User
from app.repositories.user_repository import (
    UserRepository,
)


def main() -> None:
    db = SessionLocal()

    try:
        first_name = input(
            "First name: "
        ).strip()

        last_name = input(
            "Last name: "
        ).strip()

        email = input(
            "Email: "
        ).strip().lower()

        password = getpass.getpass(
            "Password: "
        )

        confirm_password = getpass.getpass(
            "Confirm password: "
        )

        if not first_name:
            raise ValueError(
                "First name is required."
            )

        if not last_name:
            raise ValueError(
                "Last name is required."
            )

        if not email:
            raise ValueError(
                "Email is required."
            )

        if not password:
            raise ValueError(
                "Password is required."
            )

        if password != confirm_password:
            raise ValueError(
                "Passwords do not match."
            )

        repository = UserRepository()

        existing_user = (
            repository.get_by_email(
                db,
                email,
            )
        )

        if existing_user is not None:
            raise ValueError(
                "A user with this email "
                "already exists."
            )

        user = User(
            tenant_id=None,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=hash_password(
                password
            ),
            role=UserRole.SUPERADMIN,
            is_active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        print()
        print(
            "SUPERADMIN created successfully."
        )
        print(
            f"ID: {user.id}"
        )
        print(
            f"Email: {user.email}"
        )
        print(
            f"Role: {user.role.value}"
        )
        print(
            f"Tenant ID: {user.tenant_id}"
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()