from datetime import datetime
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
from app.repositories.online_eval_result_repository import (
    OnlineEvalResultRepository,
)
from app.schemas.online_eval import (
    OnlineEvalProcessRequest,
    OnlineEvalProcessResponse,
    OnlineEvalResultRead,
    OnlineEvalResultSummary,
    OnlineEvalSummaryRead,
)
from app.services.online_eval_service import (
    OnlineEvalService,
)
from app.services.online_eval_summary_service import (
    OnlineEvalSummaryService,
)


router = APIRouter(
    prefix="/online-eval",
    tags=["Online Evaluation"],
)


service = OnlineEvalService()

repository = (
    OnlineEvalResultRepository()
)

summary_service = (
    OnlineEvalSummaryService()
)


_ALLOWED_STATUSES = {
    "pending",
    "running",
    "completed",
    "failed",
}


def _require_tenant_id(
    current_user: User,
) -> UUID:
    if current_user.tenant_id is None:
        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,
            detail=
                "Tenant is required.",
        )

    return current_user.tenant_id


def _normalize_optional_text(
    value: str | None,
) -> str | None:
    if value is None:
        return None

    normalized = value.strip()

    return (
        normalized
        if normalized
        else None
    )


@router.post(
    "/process-pending",
    response_model=
        OnlineEvalProcessResponse,
)
def process_pending_online_evaluations(
    payload: OnlineEvalProcessRequest,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    """
    Process a bounded batch of pending online
    evaluation samples for the current tenant.
    """

    tenant_id = _require_tenant_id(
        current_user
    )

    try:
        return service.process_pending(
            db=db,

            tenant_id=
                tenant_id,

            limit=
                payload.limit,

            evaluator_llm_configuration_id=
                payload
                .evaluator_llm_configuration_id,
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
    "/summary",
    response_model=
        OnlineEvalSummaryRead,
)
def get_online_evaluation_summary(
    knowledge_base_id: (
        UUID | None
    ) = Query(
        default=None
    ),
    generator_provider: (
        str | None
    ) = Query(
        default=None
    ),
    generator_model: (
        str | None
    ) = Query(
        default=None
    ),
    created_from: (
        datetime | None
    ) = Query(
        default=None
    ),
    created_to: (
        datetime | None
    ) = Query(
        default=None
    ),
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    tenant_id = _require_tenant_id(
        current_user
    )

    normalized_provider = (
        _normalize_optional_text(
            generator_provider
        )
    )

    normalized_model = (
        _normalize_optional_text(
            generator_model
        )
    )

    if (
        created_from is not None
        and created_to is not None
        and created_from > created_to
    ):
        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,
            detail=(
                "created_from cannot be "
                "after created_to."
            ),
        )

    return (
        summary_service.get_summary(
            db=db,

            tenant_id=
                tenant_id,

            knowledge_base_id=
                knowledge_base_id,

            generator_provider=
                normalized_provider,

            generator_model=
                normalized_model,

            created_from=
                created_from,

            created_to=
                created_to,
        )
    )


@router.get(
    "/results",
    response_model=list[
        OnlineEvalResultSummary
    ],
)
def list_online_evaluation_results(
    knowledge_base_id: (
        UUID | None
    ) = Query(
        default=None
    ),
    evaluation_status: (
        str | None
    ) = Query(
        default=None,
        alias="status",
    ),
    generator_provider: (
        str | None
    ) = Query(
        default=None
    ),
    generator_model: (
        str | None
    ) = Query(
        default=None
    ),
    passed: (
        bool | None
    ) = Query(
        default=None
    ),
    source_trace_id: (
        str | None
    ) = Query(
        default=None
    ),
    created_from: (
        datetime | None
    ) = Query(
        default=None
    ),
    created_to: (
        datetime | None
    ) = Query(
        default=None
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    tenant_id = _require_tenant_id(
        current_user
    )

    normalized_status = (
        _normalize_optional_text(
            evaluation_status
        )
    )

    if (
        normalized_status
        is not None
        and normalized_status
        not in _ALLOWED_STATUSES
    ):
        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,
            detail=(
                "status must be one of: "
                "pending, running, "
                "completed, failed."
            ),
        )

    normalized_provider = (
        _normalize_optional_text(
            generator_provider
        )
    )

    normalized_model = (
        _normalize_optional_text(
            generator_model
        )
    )

    normalized_trace_id = (
        _normalize_optional_text(
            source_trace_id
        )
    )

    if (
        created_from is not None
        and created_to is not None
        and created_from > created_to
    ):
        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,
            detail=(
                "created_from cannot be "
                "after created_to."
            ),
        )

    try:
        return (
            repository.list_filtered(
                db=db,

                tenant_id=
                    tenant_id,

                knowledge_base_id=
                    knowledge_base_id,

                status=
                    normalized_status,

                generator_provider=
                    normalized_provider,

                generator_model=
                    normalized_model,

                passed=
                    passed,

                source_trace_id=
                    normalized_trace_id,

                created_from=
                    created_from,

                created_to=
                    created_to,

                limit=
                    limit,

                offset=
                    offset,
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
    "/results/{result_id}",
    response_model=
        OnlineEvalResultRead,
)
def get_online_evaluation_result(
    result_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    tenant_id = _require_tenant_id(
        current_user
    )

    result = (
        repository.get_for_tenant(
            db=db,
            tenant_id=
                tenant_id,
            result_id=
                result_id,
        )
    )

    if result is None:
        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,
            detail=(
                "Online evaluation result "
                "not found."
            ),
        )

    return result


@router.get(
    "/traces/{source_trace_id}",
    response_model=list[
        OnlineEvalResultSummary
    ],
)
def list_online_evaluations_by_trace(
    source_trace_id: str,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    tenant_id = _require_tenant_id(
        current_user
    )

    normalized_trace_id = (
        source_trace_id.strip()
    )

    if not normalized_trace_id:
        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,
            detail=(
                "source_trace_id is required."
            ),
        )

    return (
        repository.list_by_trace_id(
            db=db,
            tenant_id=
                tenant_id,
            source_trace_id=
                normalized_trace_id,
        )
    )
