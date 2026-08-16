from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.auth.permissions import (
    require_admin,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.agent import (
    AgentCreate,
    AgentResponse,
    AgentUpdate,
)
from app.schemas.agent_run import (
    AgentRunRequest,
    AgentRunResponse,
)
from app.services.agent_execution_service import (
    AgentExecutionService,
)
from app.services.agent_service import (
    AgentService,
)


router = APIRouter(
    prefix="/agents",
    tags=["Agents"],
)


service = AgentService()

execution_service = (
    AgentExecutionService()
)


@router.get(
    "",
    response_model=list[
        AgentResponse
    ],
)
def list_agents(
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
    )


@router.post(
    "",
    response_model=
        AgentResponse,
    status_code=
        status.HTTP_201_CREATED,
)
def create_agent(
    payload: AgentCreate,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    return service.create(
        db=db,
        current_user=current_user,
        payload=payload,
    )


@router.post(
    "/{agent_id}/run",
    response_model=
        AgentRunResponse,
)
def run_agent(
    agent_id: UUID,
    payload: AgentRunRequest,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    return (
        execution_service.run(
            db=db,
            current_user=
                current_user,
            agent_id=
                agent_id,
            query=
                payload.query,
        )
    )


@router.get(
    "/{agent_id}",
    response_model=
        AgentResponse,
)
def get_agent(
    agent_id: UUID,
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
        agent_id=agent_id,
    )


@router.put(
    "/{agent_id}",
    response_model=
        AgentResponse,
)
def update_agent(
    agent_id: UUID,
    payload: AgentUpdate,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    return service.update(
        db=db,
        current_user=current_user,
        agent_id=agent_id,
        payload=payload,
    )


@router.delete(
    "/{agent_id}",
    status_code=
        status.HTTP_204_NO_CONTENT,
)
def delete_agent(
    agent_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    service.delete(
        db=db,
        current_user=current_user,
        agent_id=agent_id,
    )

    return Response(
        status_code=
            status.HTTP_204_NO_CONTENT,
    )