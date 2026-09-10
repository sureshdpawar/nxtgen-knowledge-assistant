from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AgentEvalToolExpectation(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    input_parameters: dict = Field(default_factory=dict)


class AgentEvalDatasetCreate(BaseModel):
    agent_id: UUID
    name: str = Field(min_length=1, max_length=255)
    version: str = Field(default="v1", min_length=1, max_length=50)
    description: str | None = None


class AgentEvalDatasetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    agent_id: UUID
    name: str
    version: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class AgentEvalCaseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    input: str = Field(min_length=1)
    expected_outcome: str = Field(min_length=1)
    expected_tools: list[AgentEvalToolExpectation] = Field(default_factory=list)
    forbidden_tools: list[str] = Field(default_factory=list)
    enabled: bool = True


class AgentEvalCaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    dataset_id: UUID
    name: str
    input: str
    expected_outcome: str
    expected_tools: list[dict]
    forbidden_tools: list[str]
    enabled: bool
    source_agent_run_id: UUID | None
    created_at: datetime
    updated_at: datetime


class AgentEvalDatasetImportPayload(AgentEvalDatasetCreate):
    cases: list[AgentEvalCaseCreate] = Field(min_length=1)


class AgentEvalDatasetImportRead(BaseModel):
    dataset: AgentEvalDatasetRead
    case_count: int


class AgentEvalExperimentCreate(BaseModel):
    dataset_id: UUID
    name: str = Field(min_length=1, max_length=255)
    pass_rate_threshold: float = Field(default=0.80, ge=0.0, le=1.0)


class AgentEvalExperimentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    dataset_id: UUID
    agent_id: UUID
    name: str
    status: str
    judge_model: str | None
    pass_rate_threshold: float
    case_count: int
    passed_count: int
    pass_rate: float | None
    outcome_correctness: float | None
    tool_correctness: float | None
    argument_correctness: float | None
    metrics: dict
    created_at: datetime
    updated_at: datetime


class AgentEvalResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    experiment_id: UUID
    eval_case_id: UUID
    agent_run_id: UUID | None
    actual_answer: str | None
    tools_called: list
    outcome_correctness: float | None
    tool_correctness: float | None
    argument_correctness: float | None
    forbidden_tool_violations: list
    passed: bool | None
    metrics: dict
    judge_metadata: dict
    created_at: datetime
    updated_at: datetime
