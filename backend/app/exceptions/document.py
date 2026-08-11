from fastapi import status

from app.exceptions.base import AppException


class DocumentNotFoundError(AppException):

    def __init__(self):

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="DOCUMENT_NOT_FOUND",
            message="Document not found.",
        )