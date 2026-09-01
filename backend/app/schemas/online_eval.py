from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class OnlineEvalProcessRequest(
    BaseModel
):
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
    )

    evaluator_llm_configuration_id: (
        UUID | None
    ) = None


class OnlineEvalProcessResponse(
    BaseModel
):
    selected: int

    completed: int

    failed: int


class OnlineEvalResultRead(
    BaseModel
):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID

    tenant_id: UUID

    knowledge_base_id: (
        UUID | None
    )

    conversation_id: (
        UUID | None
    )

    message_id: (
        UUID | None
    )

    source_trace_id: str

    status: str

    sample_reason: str

    question: str

    actual_answer: str

    retrieval_context: list[str]

    generator_provider: (
        str | None
    )

    generator_model: (
        str | None
    )

    faithfulness_score: (
        float | None
    )

    answer_relevancy_score: (
        float | None
    )

    contextual_relevancy_score: (
        float | None
    )

    passed: (
        bool | None
    )

    evaluated_at: (
        datetime | None
    )

    error_message: (
        str | None
    )

    evaluation_metadata: dict[
        str,
        Any,
    ]

    created_at: datetime

    updated_at: datetime


class OnlineEvalResultSummary(
    BaseModel
):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID

    knowledge_base_id: (
        UUID | None
    )

    source_trace_id: str

    status: str

    sample_reason: str

    generator_provider: (
        str | None
    )

    generator_model: (
        str | None
    )

    faithfulness_score: (
        float | None
    )

    answer_relevancy_score: (
        float | None
    )

    contextual_relevancy_score: (
        float | None
    )

    passed: (
        bool | None
    )

    evaluated_at: (
        datetime | None
    )

    created_at: datetime



class OnlineEvalAverageScores(
    BaseModel
):
    faithfulness: (
        float | None
    )

    answer_relevancy: (
        float | None
    )

    contextual_relevancy: (
        float | None
    )


class OnlineEvalCostSummary(
    BaseModel
):
    total: (
        float | None
    )

    currency: (
        str | None
    )

    priced_evaluations: int

    unpriced_evaluations: int

    pricing_complete: bool


class OnlineEvalSummaryRead(
    BaseModel
):
    total: int

    pending: int

    running: int

    completed: int

    failed: int

    passed: int

    not_passed: int

    pass_rate: (
        float | None
    )

    average_scores: (
        OnlineEvalAverageScores
    )

    evaluation_cost: (
        OnlineEvalCostSummary
    )
