from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class AgentOnlineEvalRunRequest(BaseModel):
    evaluator_llm_configuration_id: UUID | None = None
    task_quality_threshold: float = Field(
        default=0.80,
        ge=0.0,
        le=1.0,
    )


class AgentOnlineEvalProcessRequest(BaseModel):
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
    )
    evaluator_llm_configuration_id: UUID | None = None
    task_quality_threshold: float = Field(
        default=0.80,
        ge=0.0,
        le=1.0,
    )


class AgentOnlineEvalProcessResponse(BaseModel):
    requested: int
    processed: int
    completed: int
    failed: int
    result_ids: list[UUID]


class AgentOnlineEvalResultRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    tenant_id: UUID
    agent_id: UUID
    agent_run_id: UUID

    status: str
    sample_reason: str

    question: str
    actual_answer: str | None
    tools_used: list

    task_quality_score: float | None
    execution_health_score: float | None
    overall_score: float | None

    passed: bool | None
    evaluated_at: datetime | None
    error_message: str | None

    metrics: dict
    evaluation_metadata: dict

    created_at: datetime
    updated_at: datetime


class AgentOnlineEvalSummaryRead(BaseModel):
    total: int
    pending: int
    completed: int
    failed: int
    passed: int
    failed_quality: int
    pass_rate: float | None
    average_task_quality: float | None
    average_execution_health: float | None
    average_overall_score: float | None
