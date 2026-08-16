from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.core.enums import AgentStatus


class AgentCreate(BaseModel):
    name: str

    description: str | None = None

    system_prompt: str

    llm_configuration_id:UUID | None = None

    max_iterations: int = Field(
        default=6,
        ge=1,
        le=20,
    )

    status: AgentStatus = (
        AgentStatus.DRAFT
    )

    knowledge_base_ids: list[UUID] = Field(
        default_factory=list,
    )


class AgentUpdate(BaseModel):
    name: str | None = None

    description: str | None = None

    system_prompt: str | None = None

    knowledge_base_ids: list[UUID] = Field(
        default_factory=list,
   )

    max_iterations: int | None = Field(
        default=None,
        ge=1,
        le=20,
    )

    status: AgentStatus | None = None

    knowledge_base_ids: list[UUID] = Field(
        default_factory=list,
    )


class AgentResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    tenant_id: UUID

    created_by: UUID

    name: str

    description: str | None

    system_prompt: str

    llm_configuration_id: UUID | None

    max_iterations: int

    status: AgentStatus

    knowledge_base_ids: list[UUID] = Field(
        default_factory=list,
    )

    created_at: datetime

    updated_at: datetime