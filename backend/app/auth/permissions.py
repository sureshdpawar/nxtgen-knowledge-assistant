from fastapi import Depends

from app.auth.dependencies import (
    get_current_active_user,
)
from app.core.enums import (
    UserRole,
)
from app.exceptions.auth import (
    InsufficientPermissionsError,
)
from app.models.user import (
    User,
)


def require_superadmin(
    current_user: User = Depends(
        get_current_active_user,
    ),
) -> User:

    if (
        current_user.role
        != UserRole.SUPERADMIN
    ):
        raise InsufficientPermissionsError()

    return current_user


def require_admin(
    current_user: User = Depends(
        get_current_active_user,
    ),
) -> User:

    if (
        current_user.role
        != UserRole.ADMIN
    ):
        raise InsufficientPermissionsError()

    return current_user


def require_admin_or_superadmin(
    current_user: User = Depends(
        get_current_active_user,
    ),
) -> User:

    if current_user.role not in {
        UserRole.ADMIN,
        UserRole.SUPERADMIN,
    }:
        raise InsufficientPermissionsError()

    return current_user


def require_user(
    current_user: User = Depends(
        get_current_active_user,
    ),
) -> User:

    if (
        current_user.role
        != UserRole.USER
    ):
        raise InsufficientPermissionsError()

    return current_user


def require_authenticated_user(
    current_user: User = Depends(
        get_current_active_user,
    ),
) -> User:
    return current_user