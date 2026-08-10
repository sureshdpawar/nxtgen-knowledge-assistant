from fastapi import status

from app.exceptions.base import AppException


class KnowledgeBaseNotFoundError(AppException):

    def __init__(self):
        super().__init__(
            message="Knowledge Base not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="KNOWLEDGE_BASE_NOT_FOUND",
        )