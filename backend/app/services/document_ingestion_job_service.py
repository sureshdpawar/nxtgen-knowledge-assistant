from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document_ingestion_job import DocumentIngestionJob
from app.repositories.document_ingestion_job_repository import (
    DocumentIngestionJobRepository,
)


class DocumentIngestionJobService:
    def __init__(self):
        self.repository = DocumentIngestionJobRepository()

    def enqueue(
        self,
        db: Session,
        document_id: UUID,
    ) -> DocumentIngestionJob:
        return self.repository.enqueue(
            db=db,
            document_id=document_id,
            max_attempts=settings.INGESTION_JOB_MAX_ATTEMPTS,
        )
