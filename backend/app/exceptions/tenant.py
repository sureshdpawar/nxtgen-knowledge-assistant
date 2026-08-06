from fastapi import status

from app.exceptions.base import AppException


class TenantNotFoundError(AppException):

    def __init__(self):
        super().__init__(
            message="Tenant not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="TENANT_NOT_FOUND",
        )


class DuplicateTenantSlugError(AppException):

    def __init__(self):
        super().__init__(
            message="Tenant slug already exists",
            status_code=status.HTTP_409_CONFLICT,
            error_code="TENANT_SLUG_EXISTS",
        )