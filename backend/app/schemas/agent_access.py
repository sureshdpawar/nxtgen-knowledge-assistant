from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
)


class AgentUserAccessReplaceRequest(
    BaseModel,
):
    user_ids: list[UUID] = Field(
        default_factory=list,
    )


class AgentUserAccessResponse(
    BaseModel,
):
    agent_id: UUID
    user_ids: list[UUID] = Field(
        default_factory=list,
    )
