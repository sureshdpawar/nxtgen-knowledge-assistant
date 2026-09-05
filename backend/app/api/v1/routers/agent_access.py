from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from app.auth.permissions import (
    require_admin,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.agent_access import (
    AgentUserAccessReplaceRequest,
    AgentUserAccessResponse,
)
from app.services.agent_access_service import (
    AgentAccessService,
)


router = APIRouter(
    prefix="/agents",
    tags=["Agent Access"],
)


service = AgentAccessService()


@router.get(
    "/{agent_id}/access",
    response_model=
        AgentUserAccessResponse,
)
def get_agent_access(
    agent_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    return {
        "agent_id": agent_id,
        "user_ids": service.list_user_ids(
            db=db,
            current_user=current_user,
            agent_id=agent_id,
        ),
    }


@router.put(
    "/{agent_id}/access",
    response_model=
        AgentUserAccessResponse,
)
def replace_agent_access(
    agent_id: UUID,
    payload:
        AgentUserAccessReplaceRequest,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    user_ids = (
        service.replace_user_access(
            db=db,
            current_user=current_user,
            agent_id=agent_id,
            user_ids=payload.user_ids,
        )
    )

    return {
        "agent_id": agent_id,
        "user_ids": user_ids,
    }
