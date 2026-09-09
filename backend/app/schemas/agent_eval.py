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
