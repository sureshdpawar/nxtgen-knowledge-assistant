from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.enums import (
    AgentActionApprovalStatus,
    AgentRunStatus,
)


class AgentActionApprovalDecisionRequest(
    BaseModel
):
    reason: str | None = Field(
        default=None,
        max_length=2000,
    )


class AgentActionApprovalResponse(
    BaseModel
):
    id: UUID
    tenant_id: UUID
    agent_id: UUID
    agent_run_id: UUID
    checkpoint_id: str

    actions: list[dict]

    status: AgentActionApprovalStatus

    requested_at: datetime
    decided_at: datetime | None
    decided_by_user_id: UUID | None
    decision_reason: str | None

    created_at: datetime
    updated_at: datetime

    # Read-model context for the centralized Approvals page.
    agent_name: str
    actor_type: str
    actor_id: str
    run_query: str
    run_status: AgentRunStatus
