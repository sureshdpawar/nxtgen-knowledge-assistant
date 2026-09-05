from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from app.auth.permissions import (
    require_admin,
)
from app.core.enums import (
    AgentActionApprovalStatus,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.agent_action_approval import (
    AgentActionApprovalDecisionRequest,
    AgentActionApprovalResponse,
)
from app.services.agent_action_approval_service import (
    AgentActionApprovalService,
)


router = APIRouter(
    prefix="/agent-action-approvals",
    tags=[
        "Agent Action Approvals"
    ],
)

service = (
    AgentActionApprovalService()
)


@router.get(
    "",
    response_model=list[
        AgentActionApprovalResponse
    ],
)
def list_agent_action_approvals(
    approval_status:
        AgentActionApprovalStatus
        | None = Query(
            default=None,
            alias="status",
        ),
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    return service.list(
        db=db,
        current_user=current_user,
        approval_status=
            approval_status,
    )


@router.get(
    "/{approval_id}",
    response_model=(
        AgentActionApprovalResponse
    ),
)
def get_agent_action_approval(
    approval_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    return service.get(
        db=db,
        current_user=current_user,
        approval_id=approval_id,
    )


@router.post(
    "/{approval_id}/approve",
    response_model=(
        AgentActionApprovalResponse
    ),
)
async def approve_agent_action(
    approval_id: UUID,
    payload:
        AgentActionApprovalDecisionRequest,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    return await service.approve(
        db=db,
        current_user=current_user,
        approval_id=approval_id,
        reason=payload.reason,
    )


@router.post(
    "/{approval_id}/reject",
    response_model=(
        AgentActionApprovalResponse
    ),
)
async def reject_agent_action(
    approval_id: UUID,
    payload:
        AgentActionApprovalDecisionRequest,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    return await service.reject(
        db=db,
        current_user=current_user,
        approval_id=approval_id,
        reason=payload.reason,
    )
