from fastapi import status

from app.exceptions.base import AppException


class KnowledgeBaseAccessDeniedError(
    AppException,
):
    def __init__(
        self,
        message: str = (
            "You do not have permission "
            "to manage knowledge base access."
        ),
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="KNOWLEDGE_BASE_ACCESS_DENIED",
        )


class KnowledgeBaseAccessUserNotFoundError(
    AppException,
):
    def __init__(
        self,
        message: str = "User not found.",
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="ACCESS_USER_NOT_FOUND",
        )


class KnowledgeBaseAccessKnowledgeBaseNotFoundError(
    AppException,
):
    def __init__(
        self,
        message: str = "Knowledge base not found.",
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="ACCESS_KNOWLEDGE_BASE_NOT_FOUND",
        )


class CrossTenantKnowledgeBaseAccessError(
    AppException,
):
    def __init__(
        self,
        message: str = (
            "Cross-tenant knowledge base "
            "access is not allowed."
        ),
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="CROSS_TENANT_KNOWLEDGE_BASE_ACCESS",
        )