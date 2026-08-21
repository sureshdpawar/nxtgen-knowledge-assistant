from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document_ingestion_job import (
    DocumentIngestionJob,
)
from app.repositories.document_ingestion_job_repository import (
    DocumentIngestionJobRepository,
)


class DocumentIngestionJobService:

    def __init__(self):
        self.job_repository = (
            DocumentIngestionJobRepository()
        )

    def enqueue(
        self,
        db: Session,
        document_id: UUID,
    ) -> DocumentIngestionJob:

        existing_job = (
            self.job_repository
            .get_active_for_document(
                db=db,
                document_id=document_id,
            )
        )

        if existing_job is not None:
            return existing_job

        return self.job_repository.enqueue(
            db=db,
            document_id=document_id,
            max_attempts=(
                settings
                .INGESTION_JOB_MAX_ATTEMPTS
            ),
        )