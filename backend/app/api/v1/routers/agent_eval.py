from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.auth.permissions import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.agent_eval import (
    AgentEvalCaseCreate,
    AgentEvalCaseRead,
    AgentEvalDatasetCreate,
    AgentEvalDatasetRead,
)
from app.services.agent_eval_case_service import AgentEvalCaseService
from app.services.agent_eval_dataset_service import AgentEvalDatasetService


router = APIRouter(
    prefix="/agent-eval",
    tags=["Agent Evaluation"],
)

dataset_service = AgentEvalDatasetService()
case_service = AgentEvalCaseService()


def bad_request(exc: ValueError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(exc),
    )


@router.post(
    "/datasets",
    response_model=AgentEvalDatasetRead,
    status_code=status.HTTP_201_CREATED,
)
def create_dataset(
    payload: AgentEvalDatasetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        return dataset_service.create(
            db=db,
            current_user=current_user,
            payload=payload,
        )
    except ValueError as exc:
        raise bad_request(exc) from exc


@router.get(
    "/datasets",
    response_model=list[AgentEvalDatasetRead],
)
def list_datasets(
    agent_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        return dataset_service.list(
            db=db,
            current_user=current_user,
            agent_id=agent_id,
        )
    except ValueError as exc:
        raise bad_request(exc) from exc


@router.get(
    "/datasets/{dataset_id}",
    response_model=AgentEvalDatasetRead,
)
def get_dataset(
    dataset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        dataset = dataset_service.get(
            db=db,
            current_user=current_user,
            dataset_id=dataset_id,
        )
    except ValueError as exc:
        raise bad_request(exc) from exc

    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent Evaluation dataset not found.",
        )

    return dataset


@router.post(
    "/datasets/{dataset_id}/cases",
    response_model=AgentEvalCaseRead,
    status_code=status.HTTP_201_CREATED,
)
def create_case(
    dataset_id: UUID,
    payload: AgentEvalCaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        return case_service.create(
            db=db,
            current_user=current_user,
            dataset_id=dataset_id,
            payload=payload,
        )
    except ValueError as exc:
        raise bad_request(exc) from exc


@router.get(
    "/datasets/{dataset_id}/cases",
    response_model=list[AgentEvalCaseRead],
)
def list_cases(
    dataset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        return case_service.list(
            db=db,
            current_user=current_user,
            dataset_id=dataset_id,
        )
    except ValueError as exc:
        raise bad_request(exc) from exc


@router.delete(
    "/datasets/{dataset_id}/cases/{case_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_case(
    dataset_id: UUID,
    case_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        case_service.delete(
            db=db,
            current_user=current_user,
            dataset_id=dataset_id,
            case_id=case_id,
        )
    except ValueError as exc:
        raise bad_request(exc) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
