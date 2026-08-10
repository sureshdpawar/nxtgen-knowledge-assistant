from fastapi import status

from app.exceptions.base import AppException


class KnowledgeSourceNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Knowledge source not found."