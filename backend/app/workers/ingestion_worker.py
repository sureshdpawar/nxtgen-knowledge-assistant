import logging
import signal
import socket
import time
from uuid import UUID

from app.core.config import settings
from app.db.session import SessionLocal
from app.repositories.document_ingestion_job_repository import (
    DocumentIngestionJobRepository,
)
from app.services.document_processing_service import (
    DocumentProcessingService,
)


logger = logging.getLogger(
    "nxtgen.ingestion_worker"
)


class IngestionWorker:

    def __init__(self):
        self.job_repository = (
            DocumentIngestionJobRepository()
        )

        self.processing_service = (
            DocumentProcessingService()
        )

        self.worker_id = (
            f"{socket.gethostname()}-{id(self)}"
        )

        self._running = True

    def stop(
        self,
        signum=None,
        frame=None,
    ) -> None:
        logger.info(
            "Stopping ingestion worker "
            "worker_id=%s signal=%s",
            self.worker_id,
            signum,
        )

        self._running = False

    def recover_stale_jobs(
        self,
    ) -> None:
        db = SessionLocal()

        try:
            recovered_count = (
                self.job_repository
                .recover_stale(
                    db=db,
                    stale_after_seconds=(
                        settings
                        .INGESTION_JOB_STALE_AFTER_SECONDS
                    ),
                )
            )

            if recovered_count > 0:
                logger.warning(
                    "Recovered stale ingestion jobs "
                    "count=%s",
                    recovered_count,
                )

        except Exception:
            db.rollback()

            logger.exception(
                "Failed to recover stale "
                "ingestion jobs"
            )

        finally:
            db.close()

    def claim_next_job(
        self,
    ):
        db = SessionLocal()

        try:
            return (
                self.job_repository
                .claim_next(
                    db=db,
                    worker_id=(
                        self.worker_id
                    ),
                )
            )

        except Exception:
            db.rollback()

            logger.exception(
                "Failed to claim ingestion job"
            )

            return None

        finally:
            db.close()

    def process_document(
        self,
        document_id: UUID,
    ) -> None:
        db = SessionLocal()

        try:
            self.processing_service.process(
                db=db,
                document_id=document_id,
            )

        finally:
            db.close()

    def mark_completed(
        self,
        job_id: UUID,
    ) -> None:
        db = SessionLocal()

        try:
            self.job_repository.mark_completed(
                db=db,
                job_id=job_id,
            )

        except Exception:
            db.rollback()

            logger.exception(
                "Failed to mark ingestion "
                "job completed job=%s",
                job_id,
            )

            raise

        finally:
            db.close()

    def mark_failed(
        self,
        job_id: UUID,
        exc: Exception,
    ) -> None:
        db = SessionLocal()

        try:
            error_message = (
                f"{type(exc).__name__}: {exc}"
            )

            self.job_repository.mark_failed(
                db=db,
                job_id=job_id,
                error_message=error_message,
            )

        except Exception:
            db.rollback()

            logger.exception(
                "Failed to mark ingestion "
                "job failed job=%s",
                job_id,
            )

        finally:
            db.close()

    def run(
        self,
    ) -> None:

        logger.info(
            "Ingestion worker started "
            "worker_id=%s",
            self.worker_id,
        )

        self.recover_stale_jobs()

        while self._running:

            job = self.claim_next_job()

            if job is None:
                time.sleep(
                    settings
                    .INGESTION_WORKER_POLL_SECONDS
                )

                continue

            logger.info(
                "Ingestion job claimed "
                "job=%s document=%s "
                "attempt=%s/%s",
                job.id,
                job.document_id,
                job.attempt_count,
                job.max_attempts,
            )

            try:
                self.process_document(
                    document_id=(
                        job.document_id
                    ),
                )

            except Exception as exc:
                logger.exception(
                    "Ingestion job failed "
                    "job=%s document=%s",
                    job.id,
                    job.document_id,
                )

                self.mark_failed(
                    job_id=job.id,
                    exc=exc,
                )

                continue

            try:
                self.mark_completed(
                    job_id=job.id,
                )

                logger.info(
                    "Ingestion job completed "
                    "job=%s document=%s",
                    job.id,
                    job.document_id,
                )

            except Exception:
                logger.exception(
                    "Document processed but "
                    "job completion update failed "
                    "job=%s document=%s",
                    job.id,
                    job.document_id,
                )


def main() -> None:

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s "
            "%(levelname)s "
            "%(name)s "
            "%(message)s"
        ),
    )

    worker = IngestionWorker()

    signal.signal(
        signal.SIGTERM,
        worker.stop,
    )

    signal.signal(
        signal.SIGINT,
        worker.stop,
    )

    worker.run()


if __name__ == "__main__":
    main()