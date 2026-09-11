from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from app.auth.permissions import (
    require_admin,
    require_authenticated_user,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.agent_a2a_connection import (
    AgentA2AConnectionResponse,
    AgentA2AConnectionsUpdate,
)
from app.services.agent_a2a_connection_service import (
    AgentA2AConnectionService,
)


router = APIRouter(
    prefix="/agents",
    tags=["Agent A2A Connections"],
)

service = AgentA2AConnectionService()


@router.get(
    "/{agent_id}/connected-agents",
    response_model=list[AgentA2AConnectionResponse],
)
def list_agent_connections(
    agent_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_authenticated_user,
    ),
):
    return service.list(
        db=db,
        current_user=current_user,
        agent_id=agent_id,
    )


@router.put(
    "/{agent_id}/connected-agents",
    response_model=list[AgentA2AConnectionResponse],
)
def replace_agent_connections(
    agent_id: UUID,
    payload: AgentA2AConnectionsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return service.replace(
        db=db,
        current_user=current_user,
        agent_id=agent_id,
        target_agent_ids=payload.target_agent_ids,
    )
