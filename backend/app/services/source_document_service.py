from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import DocumentStatus
from app.models.document import Document
from app.models.knowledge_source import (
    KnowledgeSource,
)
from app.models.user import User
from app.repositories.document_repository import (
    DocumentRepository,
)
from app.services.document_ingestion_job_service import (
    DocumentIngestionJobService,
)
from app.sources.source_item import (
    SourceItem,
)


class SourceDocumentService:

    def __init__(self):
        self.document_repository = (
            DocumentRepository()
        )

        self.job_service = (
            DocumentIngestionJobService()
        )

    def get_existing_document(
        self,
        db: Session,
        knowledge_source_id: UUID,
        external_id: str,
    ) -> Document | None:

        return (
            self.document_repository
            .get_by(
                db,
                knowledge_source_id=(
                    knowledge_source_id
                ),
                external_id=external_id,
            )
        )

    def create_document(
        self,
        db: Session,
        current_user: User,
        knowledge_source: KnowledgeSource,
        item: SourceItem,
    ) -> Document:

        if item.content is None:
            raise ValueError(
                "Source item does not "
                "contain content."
            )

        document = Document(
            knowledge_source_id=(
                knowledge_source.id
            ),
            uploaded_by=(
                current_user.id
            ),
            original_filename=(
                self._get_original_filename(
                    item
                )
            ),
            stored_filename="",
            mime_type=(
                item.mime_type
            ),
            file_size=0,
            checksum=(
                item.checksum
            ),
            storage_path="",
            external_id=(
                item.external_id
            ),
            status=(
                DocumentStatus.PENDING
            ),
        )

        self.document_repository.create(
            db,
            document,
        )

        stored_filename = (
            self._get_stored_filename(
                document=document,
                item=item,
            )
        )

        storage_key = (
            Path(
                str(
                    knowledge_source
                    .knowledge_base
                    .tenant_id
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

        full_path = (
            Path(
                settings
                .DOCUMENT_STORAGE_PATH
            )
            / storage_key
        )

        full_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        full_path.write_bytes(
            item.content
        )

        document.stored_filename = (
            stored_filename
        )

        document.storage_path = (
            str(
                storage_key
            )
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

    def replace_document_content(
        self,
        db: Session,
        document: Document,
        item: SourceItem,
    ) -> Document:

        if item.content is None:
            raise ValueError(
                "Source item does not "
                "contain content."
            )

        old_full_path = (
            Path(
                settings
                .DOCUMENT_STORAGE_PATH
            )
            / document.storage_path
        )

        original_filename = (
            self._get_original_filename(
                item
            )
        )

        new_extension = (
            Path(
                original_filename
            )
            .suffix
            .lower()
        )

        if not new_extension:
            new_extension = (
                self._extension_for_mime_type(
                    item.mime_type
                )
            )

        new_stored_filename = (
            f"{document.id}"
            f"{new_extension}"
        )

        old_storage_key = (
            Path(
                document.storage_path
            )
        )

        new_storage_key = (
            old_storage_key.parent
            / new_stored_filename
        )

        new_full_path = (
            Path(
                settings
                .DOCUMENT_STORAGE_PATH
            )
            / new_storage_key
        )

        new_full_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        new_full_path.write_bytes(
            item.content
        )

        if (
            old_full_path
            != new_full_path
            and old_full_path.exists()
        ):
            old_full_path.unlink()

        document.original_filename = (
            original_filename
        )

        document.stored_filename = (
            new_stored_filename
        )

        document.storage_path = (
            str(
                new_storage_key
            )
        )

        document.mime_type = (
            item.mime_type
        )

        document.file_size = (
            new_full_path
            .stat()
            .st_size
        )

        document.checksum = (
            item.checksum
        )

        document.status = (
            DocumentStatus.PENDING
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

    def retry_document(
        self,
        db: Session,
        document: Document,
    ) -> Document:

        document.status = (
            DocumentStatus.PENDING
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

    def _get_original_filename(
        self,
        item: SourceItem,
    ) -> str:

        if item.filename:
            return item.filename

        safe_title = (
            item.title
            .strip()
            .replace(
                "/",
                "-",
            )
            .replace(
                "\\",
                "-",
            )
        )

        if not safe_title:
            safe_title = (
                "source-document"
            )

        extension = (
            self._extension_for_mime_type(
                item.mime_type
            )
        )

        return (
            f"{safe_title}"
            f"{extension}"
        )

    def _get_stored_filename(
        self,
        document: Document,
        item: SourceItem,
    ) -> str:

        original_filename = (
            self._get_original_filename(
                item
            )
        )

        extension = (
            Path(
                original_filename
            )
            .suffix
            .lower()
        )

        if not extension:
            extension = (
                self._extension_for_mime_type(
                    item.mime_type
                )
            )

        return (
            f"{document.id}"
            f"{extension}"
        )

    def _extension_for_mime_type(
        self,
        mime_type: str,
    ) -> str:

        mapping = {
            "application/pdf":
                ".pdf",

            "application/msword":
                ".doc",

            "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                ".docx",

            "application/vnd.ms-powerpoint":
                ".ppt",

            "application/vnd.openxmlformats-officedocument.presentationml.presentation":
                ".pptx",

            "application/vnd.ms-excel":
                ".xls",

            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                ".xlsx",

            "text/plain":
                ".txt",

            "text/html":
                ".html",

            "text/markdown":
                ".md",

            "text/csv":
                ".csv",
        }

        return (
            mapping.get(
                mime_type,
                ".bin",
            )
        )