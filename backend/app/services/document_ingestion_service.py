from pathlib import Path
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import DocumentStatus
from app.exceptions.knowledge_source import (
    KnowledgeSourceNotFoundError,
)
from app.models.document import Document
from app.models.user import User
from app.repositories.document_repository import (
    DocumentRepository,
)
from app.repositories.knowledge_source_repository import (
    KnowledgeSourceRepository,
)
from app.services.document_ingestion_job_service import (
    DocumentIngestionJobService,
)
from app.storage.local_document_store import (
    LocalDocumentStore,
)
from app.utils.file_utils import checksum


class DocumentIngestionService:

    def __init__(self):
        self.document_repository = (
            DocumentRepository()
        )

        self.knowledge_source_repository = (
            KnowledgeSourceRepository()
        )

        self.job_service = (
            DocumentIngestionJobService()
        )

        self.document_store = (
            LocalDocumentStore()
        )

    def upload(
        self,
        db: Session,
        current_user: User,
        knowledge_source_id: UUID,
        file: UploadFile,
    ) -> Document:

        knowledge_source = (
            self.knowledge_source_repository.get(
                db,
                knowledge_source_id,
            )
        )

        if (
            knowledge_source is None
            or knowledge_source
            .knowledge_base
            .tenant_id
            != current_user.tenant_id
        ):
            raise KnowledgeSourceNotFoundError()

        file_checksum = checksum(
            file
        )

        document = Document(
            knowledge_source_id=(
                knowledge_source.id
            ),
            uploaded_by=(
                current_user.id
            ),
            original_filename=(
                file.filename
            ),
            stored_filename="",
            mime_type=(
                file.content_type
            ),
            file_size=0,
            checksum=(
                file_checksum
            ),
            storage_path="",
            status=(
                DocumentStatus.PENDING
            ),
        )

        self.document_repository.create(
            db,
            document,
        )

        extension = (
            Path(
                file.filename
            )
            .suffix
            .lower()
        )

        stored_filename = (
            f"{document.id}{extension}"
        )

        storage_key = (
            Path(
                str(
                    current_user.tenant_id
                )
            )
            / str(
                knowledge_source
                .knowledge_base
                .id
            )
            / str(
                knowledge_source.id
            )
            / stored_filename
        )

        self.document_store.save(
            str(
                storage_key
            ),
            file,
        )

        document.stored_filename = (
            stored_filename
        )

        document.storage_path = (
            str(
                storage_key
            )
        )

        full_path = (
            Path(
                settings
                .DOCUMENT_STORAGE_PATH
            )
            / storage_key
        )

        document.file_size = (
            full_path
            .stat()
            .st_size
        )

        self.document_repository.update(
            db,
            document,
        )

        self.job_service.enqueue(
            db=db,
            document_id=(
                document.id
            ),
        )

        return document