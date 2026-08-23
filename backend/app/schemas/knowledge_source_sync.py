from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
)

from app.core.enums import (
    KnowledgeSourceSyncStatus,
)


class KnowledgeSourceSyncResponse(
    BaseModel
):
    id: UUID

    knowledge_source_id: UUID

    triggered_by: UUID

    status: (
        KnowledgeSourceSyncStatus
    )

    started_at: (
        datetime
        | None
    )

    completed_at: (
        datetime
        | None
    )

    items_discovered: int

    items_new: int

    items_changed: int

    items_unchanged: int

    items_missing: int

    items_failed: int

    error_message: (
        str
        | None
    )

    provider_summary: (
        str
        | None
    )

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )