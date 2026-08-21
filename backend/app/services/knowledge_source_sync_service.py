from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.enums import (
    DocumentStatus,
    KnowledgeSourceStatus,
    KnowledgeSourceSyncStatus,
)
from app.exceptions.knowledge_source import KnowledgeSourceNotFoundError
from app.models.knowledge_source import KnowledgeSource
from app.models.knowledge_source_sync import KnowledgeSourceSync
from app.models.user import User
from app.repositories.knowledge_source_repository import (
    KnowledgeSourceRepository,
)
from app.repositories.knowledge_source_sync_repository import (
    KnowledgeSourceSyncRepository,
)
from app.services.document_service import DocumentService
from app.services.source_document_service import SourceDocumentService
from app.sources.registry import provider_registry


class KnowledgeSourceSyncService:
    def __init__(self):
        self.source_repository = KnowledgeSourceRepository()
        self.sync_repository = KnowledgeSourceSyncRepository()
        self.source_document_service = SourceDocumentService()
        self.document_service = DocumentService()

    def sync(
        self,
        db: Session,
        current_user: User,
        knowledge_source_id: UUID,
    ) -> KnowledgeSourceSync:
        source = self._get_source(
            db=db,
            current_user=current_user,
            knowledge_source_id=knowledge_source_id,
        )

        active_sync = self.sync_repository.get_active_for_source(
            db=db,
            knowledge_source_id=source.id,
        )

        if active_sync is not None:
            return active_sync

        sync_run = KnowledgeSourceSync(
            knowledge_source_id=source.id,
            triggered_by=current_user.id,
            status=KnowledgeSourceSyncStatus.RUNNING,
            started_at=datetime.now(timezone.utc),
        )

        self.sync_repository.create(
            db,
            sync_run,
        )

        try:
            provider = provider_registry.get(
                source.type
            )

            items = provider.discover(
                source
            )

            sync_run.items_discovered = len(
                items
            )

            seen_external_ids: set[str] = set()

            for item in items:
                try:
                    if item.external_id in seen_external_ids:
                        continue

                    seen_external_ids.add(
                        item.external_id
                    )

                    existing_document = (
                        self.source_document_service.get_existing_document(
                            db=db,
                            knowledge_source_id=source.id,
                            external_id=item.external_id,
                        )
                    )

                    #
                    # NEW
                    #
                    if existing_document is None:
                        self.source_document_service.create_document(
                            db=db,
                            current_user=current_user,
                            knowledge_source=source,
                            item=item,
                        )

                        sync_run.items_new += 1
                        continue

                    #
                    # UNCHANGED
                    #
                    if existing_document.checksum == item.checksum:
                        if (
                            existing_document.status
                            == DocumentStatus.FAILED
                        ):
                            self.source_document_service.retry_document(
                                db=db,
                                document=existing_document,
                            )

                        sync_run.items_unchanged += 1
                        continue

                    #
                    # CHANGED
                    #
                    self.source_document_service.replace_document_content(
                        db=db,
                        document=existing_document,
                        item=item,
                    )

                    sync_run.items_changed += 1

                except Exception:
                    sync_run.items_failed += 1

            #
            # MISSING
            #
            # Any previously indexed external document
            # that is no longer returned by the source
            # provider is hard-deleted.
            #
            existing_documents = list(
                source.documents
            )

            for document in existing_documents:
                if document.external_id is None:
                    continue

                if document.external_id in seen_external_ids:
                    continue

                self.document_service.delete_document_record(
                    db=db,
                    document=document,
                )

                sync_run.items_missing += 1

            now = datetime.now(
                timezone.utc
            )

            source.last_sync_at = now
            source.status = KnowledgeSourceStatus.ACTIVE

            sync_run.completed_at = now

            if sync_run.items_failed > 0:
                sync_run.status = (
                    KnowledgeSourceSyncStatus.COMPLETED_WITH_ERRORS
                )

                sync_run.provider_summary = (
                    "Sync completed with "
                    f"{sync_run.items_failed} item error(s)."
                )
            else:
                sync_run.status = (
                    KnowledgeSourceSyncStatus.COMPLETED
                )

                sync_run.provider_summary = (
                    "Sync completed successfully."
                )

            self.source_repository.update(
                db,
                source,
            )

            self.sync_repository.update(
                db,
                sync_run,
            )

            return sync_run

        except Exception as exc:
            sync_run.status = (
                KnowledgeSourceSyncStatus.FAILED
            )

            sync_run.completed_at = datetime.now(
                timezone.utc
            )

            sync_run.error_message = (
                f"{type(exc).__name__}: {exc}"
            )[:4000]

            source.status = KnowledgeSourceStatus.ERROR

            self.source_repository.update(
                db,
                source,
            )

            self.sync_repository.update(
                db,
                sync_run,
            )

            raise

    def list_syncs(
        self,
        db: Session,
        current_user: User,
        knowledge_source_id: UUID,
    ) -> list[KnowledgeSourceSync]:
        source = self._get_source(
            db=db,
            current_user=current_user,
            knowledge_source_id=knowledge_source_id,
        )

        return self.sync_repository.list_by_source(
            db=db,
            knowledge_source_id=source.id,
        )

    def _get_source(
        self,
        db: Session,
        current_user: User,
        knowledge_source_id: UUID,
    ) -> KnowledgeSource:
        source = self.source_repository.get(
            db,
            knowledge_source_id,
        )

        if (
            source is None
            or source.knowledge_base.tenant_id
            != current_user.tenant_id
        ):
            raise KnowledgeSourceNotFoundError()

        return source