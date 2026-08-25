from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
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
    EvalDatasetImportPayload,
    EvalDatasetImportRead,
    EvalDatasetRead,
    EvalExperimentRead,
    EvalExperimentRun,
    EvalResultRead,
)
from app.services.eval_case_service import (
    EvalCaseService,
)
from app.services.eval_dataset_import_service import (
    EvalDatasetImportService,
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

dataset_import_service = (
    EvalDatasetImportService()
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


@router.post(
    "/datasets/import",
    response_model=
        EvalDatasetImportRead,
    status_code=
        status.HTTP_201_CREATED,
)
async def import_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    """
    Import a complete evaluation dataset
    and all golden test cases from one
    UTF-8 JSON file.

    The import is transactional:

    - dataset created
    - all cases created
    - commit only if every case succeeds

    If any case is invalid, the entire
    import is rolled back.
    """

    filename = (
        file.filename
        or ""
    )

    if not filename.lower().endswith(
        ".json"
    ):
        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,
            detail=(
                "Evaluation dataset "
                "must be a JSON file."
            ),
        )

    try:
        raw_content = await file.read()

        if not raw_content:
            raise ValueError(
                "Uploaded JSON file "
                "is empty."
            )

        try:
            json_content = (
                raw_content.decode(
                    "utf-8"
                )
            )

        except UnicodeDecodeError as exc:
            raise ValueError(
                "Evaluation dataset "
                "must use UTF-8 encoding."
            ) from exc

        #
        # Pydantic handles:
        #
        # - JSON parsing
        # - UUID validation
        # - required fields
        # - list validation
        # - nested case validation
        #
        payload = (
            EvalDatasetImportPayload
            .model_validate_json(
                json_content
            )
        )

        dataset, case_count = (
            dataset_import_service
            .import_dataset(
                db=db,
                payload=payload,
            )
        )

        return {
            "dataset":
                dataset,

            "case_count":
                case_count,
        }

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,
            detail=str(
                exc
            ),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unable to import "
                "evaluation dataset: "
                f"{str(exc)}"
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
# Retrieval Experiments
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


#
# Full RAG Experiments
#


@router.post(
    "/experiments/rag",
    response_model=
        EvalExperimentRead,
    status_code=
        status.HTTP_201_CREATED,
)
def run_rag_experiment(
    payload: EvalExperimentRun,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    """
    Execute the full RAG pipeline against
    every test case in an evaluation dataset.

    Captures:

    - retrieval results
    - Hit@K
    - Reciprocal Rank
    - MRR
    - generated answer
    - latency
    - token usage
    - LLM configuration metadata

    LLM-as-a-Judge metrics are added later.
    """

    try:
        return (
            experiment_service
            .run_rag_experiment(
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


#
# Experiment Queries
#


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