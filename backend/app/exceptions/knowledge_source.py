from fastapi import status

from app.exceptions.base import AppException


class KnowledgeSourceNotFoundError(AppException):
    def __init__(
        self,
        message: str = "Knowledge source not found.",
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="KNOWLEDGE_SOURCE_NOT_FOUND",
        )