from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.core.enums import (
    ToolExecutionPolicy,
    ToolRiskLevel,
    ToolType,
)


class ToolDefinitionCreate(BaseModel):
    integration_id:UUID | None = None

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    description: str = Field(
        min_length=1,
    )

    tool_type: ToolType

    risk_level:ToolRiskLevel = (
            ToolRiskLevel.READ
        )

    input_schema: dict = Field(
        default_factory=dict,
    )

    configuration:dict | None = None

    is_active: bool = True


class ToolDefinitionUpdate(BaseModel):
    integration_id:UUID | None = None

    name:str | None = None

    description:str | None = None

    risk_level:ToolRiskLevel | None = None

    input_schema:dict | None = None

    configuration:dict | None = None

    is_active:bool | None = None


class ToolDefinitionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    tenant_id: UUID

    integration_id:UUID | None

    name: str
    description: str

    tool_type: ToolType

    risk_level:ToolRiskLevel

    input_schema: dict

    configuration:dict | None

    is_active: bool

    created_at: datetime
    updated_at: datetime


class AgentToolAssignRequest(BaseModel):
    tool_ids: list[UUID] = Field(
        default_factory=list,
    )


class AgentToolPolicyUpdateRequest(
    BaseModel,
):
    execution_policy: ToolExecutionPolicy


class AgentToolPolicyResponse(
    BaseModel,
):
    model_config = ConfigDict(
        from_attributes=True,
    )

    agent_id: UUID
    tool_id: UUID
    execution_policy: ToolExecutionPolicy
