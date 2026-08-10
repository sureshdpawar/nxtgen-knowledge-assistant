from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import (
    KnowledgeSourceStatus,
    KnowledgeSourceType,
)


class KnowledgeSourceCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=255,
    )

    type: KnowledgeSourceType

    configuration: dict = Field(
        default_factory=dict,
    )


class KnowledgeSourceUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    status: KnowledgeSourceStatus | None = None

    configuration: dict | None = None


class KnowledgeSourceResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    knowledge_base_id: UUID
    created_by: UUID

    name: str

    type: KnowledgeSourceType

    status: KnowledgeSourceStatus

    configuration: dict

    last_sync_at: datetime | None

    created_at: datetime
    updated_at: datetime