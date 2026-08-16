from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.core.enums import (
    AgentRunStatus,
    AgentRunStepStatus,
    AgentRunStepType,
)


class AgentRunRequest(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=10000,
    )


class AgentRunResponse(BaseModel):
    run_id: UUID
    answer: str
    status: AgentRunStatus
    llm_calls: int
    tools_used: list[str]
    duration_ms: float


class AgentRunStepResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    step_number: int
    step_type: AgentRunStepType
    status: AgentRunStepStatus
    name: str
    input_data: dict | list | None
    output_data: dict | list | None
    duration_ms: float | None
    created_at: datetime


class AgentRunListResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    tenant_id: UUID
    agent_id: UUID
    user_id: UUID

    query: str
    answer: str | None

    status: AgentRunStatus

    llm_calls: int
    tools_used: list[str]

    duration_ms: float | None

    started_at: datetime
    completed_at: datetime | None

    created_at: datetime


class AgentRunDetailResponse(
    AgentRunListResponse,
):
    error_message: str | None

    steps: list[
        AgentRunStepResponse
    ]