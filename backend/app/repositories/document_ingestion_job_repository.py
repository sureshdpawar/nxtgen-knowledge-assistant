from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import DocumentIngestionJobStatus, DocumentStatus
from app.models.document import Document
from app.models.document_ingestion_job import DocumentIngestionJob


class DocumentIngestionJobRepository:
    def enqueue(
        self,
        db: Session,
        document_id: UUID,
        max_attempts: int,
    ) -> DocumentIngestionJob:
        job = DocumentIngestionJob(
            document_id=document_id,
            status=DocumentIngestionJobStatus.PENDING,
            max_attempts=max_attempts,
        )
        db.add(job)
        db.flush()
        db.refresh(job)
        return job

    def claim_next(
        self,
        db: Session,
        worker_id: str,
    ) -> DocumentIngestionJob | None:
        now = datetime.now(timezone.utc)
        stmt = (
            select(DocumentIngestionJob)
            .where(
                DocumentIngestionJob.status
                == DocumentIngestionJobStatus.PENDING,
                DocumentIngestionJob.available_at <= now,
            )
            .order_by(DocumentIngestionJob.created_at.asc())
            .with_for_update(skip_locked=True)
            .limit(1)
        )
        job = db.execute(stmt).scalar_one_or_none()
        if job is None:
            return None

        job.status = DocumentIngestionJobStatus.PROCESSING
        job.attempt_count += 1
        job.claimed_at = now
        job.worker_id = worker_id
        job.error_message = None
        db.commit()
        db.refresh(job)
        return job

    def mark_completed(self, db: Session, job_id: UUID) -> None:
        job = db.get(DocumentIngestionJob, job_id)
        if job is None:
            return
        job.status = DocumentIngestionJobStatus.COMPLETED
        job.completed_at = datetime.now(timezone.utc)
        job.failed_at = None
        db.commit()

    def mark_failed(
        self,
        db: Session,
        job_id: UUID,
        error_message: str,
    ) -> None:
        job = db.get(DocumentIngestionJob, job_id)
        if job is None:
            return
        job.status = DocumentIngestionJobStatus.FAILED
        job.failed_at = datetime.now(timezone.utc)
        job.error_message = error_message[:4000]
        db.commit()

    def recover_stale(
        self,
        db: Session,
        stale_after_seconds: int,
    ) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(
            seconds=stale_after_seconds
        )
        stmt = (
            select(DocumentIngestionJob)
            .where(
                DocumentIngestionJob.status
                == DocumentIngestionJobStatus.PROCESSING,
                DocumentIngestionJob.claimed_at.is_not(None),
                DocumentIngestionJob.claimed_at < cutoff,
            )
            .with_for_update(skip_locked=True)
        )
        jobs = list(db.execute(stmt).scalars().all())
        now = datetime.now(timezone.utc)

        for job in jobs:
            document = db.get(Document, job.document_id)
            if document is not None and document.status == DocumentStatus.READY:
                job.status = DocumentIngestionJobStatus.COMPLETED
                job.completed_at = now
                continue

            if job.attempt_count < job.max_attempts:
                job.status = DocumentIngestionJobStatus.PENDING
                job.available_at = now
                job.claimed_at = None
                job.worker_id = None
            else:
                job.status = DocumentIngestionJobStatus.FAILED
                job.failed_at = now
                job.error_message = "Job exceeded maximum attempts after stale recovery."

        db.commit()
        return len(jobs)
