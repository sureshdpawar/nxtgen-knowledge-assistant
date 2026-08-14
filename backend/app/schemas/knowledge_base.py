from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.enums import (
    KnowledgeBaseStatus,
    KnowledgeBaseVisibility,
)


class KnowledgeBaseCreate(BaseModel):
    name: str
    description: str | None = None
    visibility: KnowledgeBaseVisibility = (
        KnowledgeBaseVisibility.PRIVATE
    )


class KnowledgeBaseUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: KnowledgeBaseStatus | None = None
    visibility: KnowledgeBaseVisibility | None = None


class KnowledgeBaseResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    tenant_id: UUID
    owner_user_id: UUID

    llm_configuration_id: UUID | None

    name: str
    description: str | None

    status: KnowledgeBaseStatus
    visibility: KnowledgeBaseVisibility

    created_at: datetime
    updated_at: datetime