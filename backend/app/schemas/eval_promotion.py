from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
)


class AgentRunEvalPromotionRequest(
    BaseModel,
):
    dataset_id: UUID

    #
    # True for normal answer cases.
    # False allows a reviewed refusal to
    # become a refusal-evaluation case.
    #
    answerable: bool = True


class AgentRunEvalPromotionResponse(
    BaseModel,
):
    eval_case_id: UUID
    dataset_id: UUID

    source_agent_run_id: UUID
    agent_id: UUID

    question: str
    expected_answer: str
    answerable: bool

    tools_used: list = Field(
        default_factory=list,
    )

    source_metadata: dict = Field(
        default_factory=dict,
    )
