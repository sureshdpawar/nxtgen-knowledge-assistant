from typing import Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
)

from app.core.enums import (
    AgentRunStatus,
)


class AgentChatRequest(
    BaseModel,
):
    agent_id: UUID

    conversation_id: UUID | None = None

    query: str = Field(
        min_length=1,
        max_length=10000,
    )


class AgentChatResumeRequest(
    BaseModel,
):
    conversation_id: UUID

    run_id: UUID

    decision: Literal[
        "approve",
        "reject",
    ]

    reason: str | None = Field(
        default=None,
        max_length=2000,
    )


class AgentChatResult(
    BaseModel,
):
    conversation_id: UUID

    agent_id: UUID

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
