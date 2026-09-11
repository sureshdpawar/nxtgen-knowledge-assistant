from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
)


class AgentA2AConnectionsUpdate(BaseModel):
    target_agent_ids: list[UUID] = Field(
        default_factory=list,
    )


class AgentA2AConnectionResponse(BaseModel):
    target_agent_id: UUID
    target_agent_name: str
    target_agent_description: str | None
    target_agent_status: str
    protocol: str = "A2A"
    protocol_version: str = "1.0"
