from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.auth.permissions import (
    require_admin,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.agent_observability import (
    AgentObservabilityResponse,
)
from app.schemas.agent_run import (
    AgentRunDetailResponse,
    AgentRunListResponse,
)
from app.schemas.eval_promotion import (
    AgentRunEvalPromotionRequest,
    AgentRunEvalPromotionResponse,
)
from app.services.agent_observability_service import (
    AgentObservabilityService,
)
from app.services.agent_run_service import (
    AgentRunService,
)
from app.services.eval_promotion_service import (
    EvalPromotionService,
)


router = APIRouter(
    prefix="/agent-runs",
    tags=["Agent Runs"],
)


service = AgentRunService()

observability_service = (
    AgentObservabilityService()
)

promotion_service = (
    EvalPromotionService()
)


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
    "/agent/{agent_id}/metrics",
    response_model=
        AgentObservabilityResponse,
)
def get_agent_metrics(
    agent_id: UUID,
    hours: int = Query(
        default=24,
        ge=1,
        le=720,
    ),
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    return (
        observability_service
        .get_agent_metrics(
            db=db,
            current_user=current_user,
            agent_id=agent_id,
            hours=hours,
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


@router.post(
    "/{run_id}/promote-to-eval",
    response_model=
        AgentRunEvalPromotionResponse,
    status_code=
        status.HTTP_201_CREATED,
)
def promote_agent_run_to_eval(
    run_id: UUID,
    payload:
        AgentRunEvalPromotionRequest,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    return promotion_service.promote(
        db=db,
        current_user=current_user,
        run_id=run_id,
        payload=payload,
    )
