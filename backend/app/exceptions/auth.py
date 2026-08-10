from fastapi import status

from app.exceptions.base import AppException


class InvalidCredentialsError(AppException):

    def __init__(self):
        super().__init__(
            message="Invalid email or password.",
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="INVALID_CREDENTIALS",
        )


class InactiveUserError(AppException):

    def __init__(self):
        super().__init__(
            message="User account is inactive.",
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="USER_INACTIVE",
        )


class InsufficientPermissionsError(AppException):

    def __init__(self):
        super().__init__(
            message="You do not have permission to perform this action.",
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="INSUFFICIENT_PERMISSIONS",
        )