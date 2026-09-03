from datetime import datetime
from typing import Literal
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

    # Omit to start a new LangGraph thread.
    # Reuse to continue a conversation.
    thread_id: UUID | None = None


class AgentResumeRequest(BaseModel):
    decision: Literal[
        "approve",
        "reject",
    ]

    reason: str | None = Field(
        default=None,
        max_length=2000,
    )


class AgentRunResponse(BaseModel):
    run_id: UUID
    thread_id: UUID
    checkpoint_id: str | None
    answer: str | None
    status: AgentRunStatus
    llm_calls: int
    tools_used: list[str]
    duration_ms: float
    interrupts: list[dict] = Field(
        default_factory=list,
    )


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
    user_id: UUID | None
    actor_type: str
    actor_id: str
    context_metadata: dict | None
    thread_id: UUID | None
    checkpoint_id: str | None

    query: str
    answer: str | None

    status: AgentRunStatus

    llm_calls: int
    tools_used: list[str]

    duration_ms: float | None

    started_at: datetime
    completed_at: datetime | None

    created_at: datetime


class AgentRunUsageResponse(
    BaseModel,
):
    request_count: int

    input_tokens: int
    output_tokens: int
    total_tokens: int

    estimated_cost: float | None
    currency: str | None

    pricing_complete: bool


class AgentRunDetailResponse(
    AgentRunListResponse,
):
    error_message: str | None

    usage: AgentRunUsageResponse

    steps: list[
        AgentRunStepResponse
    ]


class AgentGraphStateResponse(BaseModel):
    checkpoint_id: str | None
    next: list[str] = Field(default_factory=list)
    created_at: str | None = None
    metadata: dict = Field(default_factory=dict)
    interrupts: list[dict] = Field(default_factory=list)
    state: dict = Field(default_factory=dict)


class AgentCheckpointHistoryResponse(BaseModel):
    thread_id: UUID
    checkpoints: list[AgentGraphStateResponse] = Field(
        default_factory=list,
    )
