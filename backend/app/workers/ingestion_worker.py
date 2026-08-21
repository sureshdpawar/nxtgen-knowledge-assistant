import logging
import signal
import socket
import time
import uuid

from app.core.config import settings
from app.db.session import SessionLocal
from app.repositories.document_ingestion_job_repository import (
    DocumentIngestionJobRepository,
)
from app.services.document_processing_service import DocumentProcessingService


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_shutdown_requested = False


def _request_shutdown(signum, frame) -> None:
    global _shutdown_requested
    _shutdown_requested = True
    logger.info("Shutdown requested for ingestion worker")


def _worker_id() -> str:
    return f"{socket.gethostname()}-{uuid.uuid4().hex[:8]}"


def _recover_stale_jobs(repository: DocumentIngestionJobRepository) -> None:
    with SessionLocal() as db:
        recovered = repository.recover_stale(
            db=db,
            stale_after_seconds=settings.INGESTION_JOB_STALE_AFTER_SECONDS,
        )
        if recovered:
            logger.info("Recovered %s stale ingestion job(s)", recovered)


def _claim_next_job(repository: DocumentIngestionJobRepository, worker_id: str):
    with SessionLocal() as db:
        job = repository.claim_next(db=db, worker_id=worker_id)
        if job is None:
            return None
        return job.id, job.document_id


def _mark_completed(repository: DocumentIngestionJobRepository, job_id) -> None:
    with SessionLocal() as db:
        repository.mark_completed(db=db, job_id=job_id)


def _mark_failed(
    repository: DocumentIngestionJobRepository,
    job_id,
    exc: Exception,
) -> None:
    with SessionLocal() as db:
        repository.mark_failed(
            db=db,
            job_id=job_id,
            error_message=f"{type(exc).__name__}: {exc}",
        )


def run() -> None:
    signal.signal(signal.SIGTERM, _request_shutdown)
    signal.signal(signal.SIGINT, _request_shutdown)

    worker_id = _worker_id()
    repository = DocumentIngestionJobRepository()
    processing_service = DocumentProcessingService()

    logger.info("Starting ingestion worker %s", worker_id)
    _recover_stale_jobs(repository)

    while not _shutdown_requested:
        claimed = _claim_next_job(repository, worker_id)
        if claimed is None:
            time.sleep(settings.INGESTION_WORKER_POLL_SECONDS)
            continue

        job_id, document_id = claimed
        logger.info("Processing ingestion job %s for document %s", job_id, document_id)

        try:
            with SessionLocal() as processing_db:
                processing_service.process(
                    db=processing_db,
                    document_id=document_id,
                )
        except Exception as exc:
            logger.exception("Ingestion job %s failed", job_id)
            _mark_failed(repository, job_id, exc)
        else:
            _mark_completed(repository, job_id)
            logger.info("Completed ingestion job %s", job_id)

    logger.info("Ingestion worker %s stopped", worker_id)


if __name__ == "__main__":
    run()
