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
from app.schemas.agent_run import (
    AgentRunDetailResponse,
    AgentRunListResponse,
)
from app.services.agent_run_service import (
    AgentRunService,
)


router = APIRouter(
    prefix="/agent-runs",
    tags=["Agent Runs"],
)


service = AgentRunService()


@router.get(
    "/agent/{agent_id}",
    response_model=list[
        AgentRunListResponse
    ],
)
def list_agent_runs(
    agent_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    return (
        service.list_for_agent(
            db=db,
            current_user=
                current_user,
            agent_id=
                agent_id,
        )
    )


@router.get(
    "/{run_id}",
    response_model=
        AgentRunDetailResponse,
)
def get_agent_run(
    run_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    return service.get(
        db=db,
        current_user=
            current_user,
        run_id=
            run_id,
    )