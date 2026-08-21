from datetime import (
    datetime,
    timedelta,
    timezone,
)
from uuid import UUID

from sqlalchemy import (
    and_,
    func,
    or_,
    select,
)
from sqlalchemy.orm import Session

from app.core.enums import (
    DocumentIngestionJobStatus,
    DocumentStatus,
)
from app.models.document import Document
from app.models.document_ingestion_job import (
    DocumentIngestionJob,
)


class DocumentIngestionJobRepository:

    def enqueue(
        self,
        db: Session,
        document_id: UUID,
        max_attempts: int = 3,
    ) -> DocumentIngestionJob:

        job = DocumentIngestionJob(
            document_id=document_id,
            status=(
                DocumentIngestionJobStatus.PENDING
            ),
            attempt_count=0,
            max_attempts=max_attempts,
        )

        db.add(job)
        db.flush()
        db.refresh(job)

        return job

    def get(
        self,
        db: Session,
        job_id: UUID,
    ) -> DocumentIngestionJob | None:
        return db.get(
            DocumentIngestionJob,
            job_id,
        )

    def get_active_for_document(
        self,
        db: Session,
        document_id: UUID,
    ) -> DocumentIngestionJob | None:

        stmt = (
            select(DocumentIngestionJob)
            .where(
                DocumentIngestionJob.document_id
                == document_id,
                DocumentIngestionJob.status.in_(
                    [
                        DocumentIngestionJobStatus.PENDING,
                        DocumentIngestionJobStatus.PROCESSING,
                    ]
                ),
            )
            .order_by(
                DocumentIngestionJob.created_at.desc()
            )
        )

        return (
            db.execute(stmt)
            .scalars()
            .first()
        )

    def claim_next(
        self,
        db: Session,
        worker_id: str,
    ) -> DocumentIngestionJob | None:

        stmt = (
            select(DocumentIngestionJob)
            .where(
                DocumentIngestionJob.status
                == DocumentIngestionJobStatus.PENDING,
                DocumentIngestionJob.available_at
                <= func.now(),
                DocumentIngestionJob.attempt_count
                < DocumentIngestionJob.max_attempts,
            )
            .order_by(
                DocumentIngestionJob.created_at.asc()
            )
            .with_for_update(
                skip_locked=True,
            )
            .limit(1)
        )

        job = (
            db.execute(stmt)
            .scalars()
            .first()
        )

        if job is None:
            return None

        job.status = (
            DocumentIngestionJobStatus.PROCESSING
        )

        job.attempt_count += 1

        job.claimed_at = datetime.now(
            timezone.utc
        )

        job.worker_id = worker_id

        job.error_message = None

        db.commit()
        db.refresh(job)

        return job

    def mark_completed(
        self,
        db: Session,
        job_id: UUID,
    ) -> DocumentIngestionJob | None:

        job = self.get(
            db=db,
            job_id=job_id,
        )

        if job is None:
            return None

        now = datetime.now(
            timezone.utc
        )

        job.status = (
            DocumentIngestionJobStatus.COMPLETED
        )

        job.completed_at = now
        job.failed_at = None
        job.error_message = None

        db.commit()
        db.refresh(job)

        return job

    def mark_failed(
        self,
        db: Session,
        job_id: UUID,
        error_message: str,
    ) -> DocumentIngestionJob | None:

        job = self.get(
            db=db,
            job_id=job_id,
        )

        if job is None:
            return None

        job.status = (
            DocumentIngestionJobStatus.FAILED
        )

        job.failed_at = datetime.now(
            timezone.utc
        )

        job.error_message = (
            error_message[:4000]
            if error_message
            else "Unknown ingestion error"
        )

        db.commit()
        db.refresh(job)

        return job

    def recover_stale(
        self,
        db: Session,
        stale_after_seconds: int,
    ) -> int:

        stale_before = (
            datetime.now(timezone.utc)
            - timedelta(
                seconds=stale_after_seconds
            )
        )

        stmt = (
            select(DocumentIngestionJob)
            .where(
                DocumentIngestionJob.status
                == DocumentIngestionJobStatus.PROCESSING,
                or_(
                    DocumentIngestionJob.claimed_at
                    < stale_before,
                    DocumentIngestionJob.claimed_at
                    .is_(None),
                ),
            )
            .with_for_update(
                skip_locked=True,
            )
        )

        jobs = (
            db.execute(stmt)
            .scalars()
            .all()
        )

        recovered_count = 0

        for job in jobs:

            document = db.get(
                Document,
                job.document_id,
            )

            if (
                document is not None
                and document.status
                == DocumentStatus.READY
            ):
                job.status = (
                    DocumentIngestionJobStatus.COMPLETED
                )

                job.completed_at = (
                    datetime.now(
                        timezone.utc
                    )
                )

                job.error_message = None

            elif (
                job.attempt_count
                < job.max_attempts
            ):
                job.status = (
                    DocumentIngestionJobStatus.PENDING
                )

                job.available_at = (
                    datetime.now(
                        timezone.utc
                    )
                )

                job.claimed_at = None
                job.worker_id = None

                job.error_message = (
                    "Recovered stale ingestion job."
                )

            else:
                job.status = (
                    DocumentIngestionJobStatus.FAILED
                )

                job.failed_at = (
                    datetime.now(
                        timezone.utc
                    )
                )

                job.error_message = (
                    "Ingestion job exceeded "
                    "maximum retry attempts "
                    "after stale recovery."
                )

            recovered_count += 1

        db.commit()

        return recovered_count