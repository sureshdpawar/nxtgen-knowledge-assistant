from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AgentObservabilityCount(BaseModel):
    name: str
    count: int


class AgentObservabilityUsage(BaseModel):
    request_count: int
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: float | None
    currency: str | None
    pricing_complete: bool


class AgentObservabilityResponse(BaseModel):
    agent_id: UUID

    window_start: datetime
    window_end: datetime
    window_hours: int

    total_runs: int
    completed_runs: int
    failed_runs: int
    running_runs: int
    waiting_for_approval_runs: int

    completion_rate: float
    failure_rate: float

    average_duration_ms: float | None
    p95_duration_ms: float | None

    total_llm_calls: int
    average_llm_calls_per_run: float

    runs_using_tools: int
    tool_usage: list[AgentObservabilityCount] = Field(
        default_factory=list,
    )

    actor_mix: list[AgentObservabilityCount] = Field(
        default_factory=list,
    )

    llm_usage: AgentObservabilityUsage
