from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.auth.permissions import (
    require_admin,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.agent_online_eval import (
    AgentOnlineEvalProcessRequest,
    AgentOnlineEvalProcessResponse,
    AgentOnlineEvalResultRead,
    AgentOnlineEvalRunRequest,
    AgentOnlineEvalSummaryRead,
)
from app.services.agent_online_eval_service import (
    AgentOnlineEvalService,
)


router = APIRouter(
    prefix="/agent-eval/online",
    tags=["Agent Online Evaluation"],
)

service = AgentOnlineEvalService()


def _bad_request(
    exc: Exception,
) -> HTTPException:
    return HTTPException(
        status_code=
            status.HTTP_400_BAD_REQUEST,
        detail=str(exc),
    )


@router.post(
    "/process-pending",
    response_model=
        AgentOnlineEvalProcessResponse,
)
def process_pending_agent_online_evals(
    payload: AgentOnlineEvalProcessRequest,
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        require_admin
    ),
):
    try:
        return service.process_pending(
            db=db,
            current_user=current_user,
            limit=payload.limit,
            evaluator_llm_configuration_id=(
                payload
                .evaluator_llm_configuration_id
            ),
            task_quality_threshold=(
                payload
                .task_quality_threshold
            ),
        )

    except ValueError as exc:
        raise _bad_request(
            exc
        ) from exc


@router.post(
    "/runs/{agent_run_id}/evaluate",
    response_model=
        AgentOnlineEvalResultRead,
)
def evaluate_agent_run(
    agent_run_id: UUID,
    payload: AgentOnlineEvalRunRequest,
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        require_admin
    ),
):
    try:
        return service.evaluate_run(
            db=db,
            current_user=current_user,
            agent_run_id=agent_run_id,
            evaluator_llm_configuration_id=(
                payload
                .evaluator_llm_configuration_id
            ),
            task_quality_threshold=(
                payload
                .task_quality_threshold
            ),
        )

    except ValueError as exc:
        raise _bad_request(
            exc
        ) from exc


@router.get(
    "/results",
    response_model=list[
        AgentOnlineEvalResultRead
    ],
)
def list_agent_online_results(
    agent_id: UUID | None = Query(
        default=None
    ),
    passed: bool | None = Query(
        default=None
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        require_admin
    ),
):
    try:
        return service.list_results(
            db=db,
            current_user=current_user,
            agent_id=agent_id,
            passed=passed,
            limit=limit,
        )

    except ValueError as exc:
        raise _bad_request(
            exc
        ) from exc


@router.get(
    "/results/{result_id}",
    response_model=
        AgentOnlineEvalResultRead,
)
def get_agent_online_result(
    result_id: UUID,
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        require_admin
    ),
):
    try:
        result = service.get_result(
            db=db,
            current_user=current_user,
            result_id=result_id,
        )

    except ValueError as exc:
        raise _bad_request(
            exc
        ) from exc

    if result is None:
        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,
            detail=(
                "Agent online evaluation "
                "result not found."
            ),
        )

    return result


@router.get(
    "/summary",
    response_model=
        AgentOnlineEvalSummaryRead,
)
def get_agent_online_summary(
    agent_id: UUID | None = Query(
        default=None
    ),
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        require_admin
    ),
):
    try:
        return service.summary(
            db=db,
            current_user=current_user,
            agent_id=agent_id,
        )

    except ValueError as exc:
        raise _bad_request(
            exc
        ) from exc
