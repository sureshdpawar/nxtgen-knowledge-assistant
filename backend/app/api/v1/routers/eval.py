from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.auth.permissions import (
    require_admin,
)
from app.db.session import get_db
from app.models.user import User
from app.repositories.eval_result_repository import (
    EvalResultRepository,
)
from app.schemas.eval import (
    EvalCaseCreate,
    EvalCaseRead,
    EvalDatasetCreate,
    EvalDatasetRead,
    EvalExperimentRead,
    EvalExperimentRun,
    EvalResultRead,
)
from app.services.eval_case_service import (
    EvalCaseService,
)
from app.services.eval_dataset_service import (
    EvalDatasetService,
)
from app.services.eval_experiment_service import (
    EvalExperimentService,
)


router = APIRouter(
    prefix="/eval",
    tags=["Evaluation"],
)


dataset_service = (
    EvalDatasetService()
)

case_service = (
    EvalCaseService()
)

experiment_service = (
    EvalExperimentService()
)

result_repository = (
    EvalResultRepository()
)


#
# Datasets
#


@router.post(
    "/datasets",
    response_model=
        EvalDatasetRead,
    status_code=
        status.HTTP_201_CREATED,
)
def create_dataset(
    payload: EvalDatasetCreate,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    try:
        return (
            dataset_service.create(
                db=db,
                payload=payload,
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,
            detail=str(
                exc
            ),
        ) from exc


@router.get(
    "/knowledge-bases/"
    "{knowledge_base_id}/datasets",
    response_model=list[
        EvalDatasetRead
    ],
)
def list_datasets(
    knowledge_base_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    return (
        dataset_service
        .list_by_knowledge_base_id(
            db=db,
            knowledge_base_id=
                knowledge_base_id,
        )
    )


@router.get(
    "/datasets/{dataset_id}",
    response_model=
        EvalDatasetRead,
)
def get_dataset(
    dataset_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    dataset = (
        dataset_service.get(
            db=db,
            dataset_id=
                dataset_id,
        )
    )

    if dataset is None:
        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,
            detail=(
                "Eval dataset "
                "not found."
            ),
        )

    return dataset


#
# Cases
#


@router.post(
    "/cases",
    response_model=
        EvalCaseRead,
    status_code=
        status.HTTP_201_CREATED,
)
def create_case(
    payload: EvalCaseCreate,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    try:
        return (
            case_service.create(
                db=db,
                payload=payload,
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,
            detail=str(
                exc
            ),
        ) from exc


@router.get(
    "/datasets/{dataset_id}/cases",
    response_model=list[
        EvalCaseRead
    ],
)
def list_cases(
    dataset_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    return (
        case_service
        .list_by_dataset_id(
            db=db,
            dataset_id=
                dataset_id,
        )
    )


#
# Experiments
#


@router.post(
    "/experiments/retrieval",
    response_model=
        EvalExperimentRead,
    status_code=
        status.HTTP_201_CREATED,
)
def run_retrieval_experiment(
    payload: EvalExperimentRun,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    try:
        return (
            experiment_service
            .run_retrieval_experiment(
                db=db,
                dataset_id=
                    payload.dataset_id,
                knowledge_base_id=
                    payload
                    .knowledge_base_id,
                name=
                    payload.name,
                top_k=
                    payload.top_k,
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,
            detail=str(
                exc
            ),
        ) from exc


@router.get(
    "/datasets/{dataset_id}/experiments",
    response_model=list[
        EvalExperimentRead
    ],
)
def list_experiments(
    dataset_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    return (
        experiment_service
        .list_by_dataset_id(
            db=db,
            dataset_id=
                dataset_id,
        )
    )


@router.get(
    "/experiments/{experiment_id}",
    response_model=
        EvalExperimentRead,
)
def get_experiment(
    experiment_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    experiment = (
        experiment_service.get(
            db=db,
            experiment_id=
                experiment_id,
        )
    )

    if experiment is None:
        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,
            detail=(
                "Eval experiment "
                "not found."
            ),
        )

    return experiment


#
# Results
#


@router.get(
    "/experiments/"
    "{experiment_id}/results",
    response_model=list[
        EvalResultRead
    ],
)
def list_results(
    experiment_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    experiment = (
        experiment_service.get(
            db=db,
            experiment_id=
                experiment_id,
        )
    )

    if experiment is None:
        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,
            detail=(
                "Eval experiment "
                "not found."
            ),
        )

    return (
        result_repository
        .list_by_experiment_id(
            db=db,
            experiment_id=
                experiment_id,
        )
    )