from datetime import (
    date,
    timedelta,
    timezone,
    datetime,
)
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
from app.schemas.cost_analytics import (
    CostAnalyticsResponse,
)
from app.services.cost_analytics_service import (
    CostAnalyticsService,
)


router = APIRouter(
    prefix="/cost-analytics",
    tags=["Cost Analytics"],
)


service = (
    CostAnalyticsService()
)


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


@router.get(
    "",
    response_model=
        CostAnalyticsResponse,
)
def get_cost_analytics(
    start_date: (
        date | None
    ) = Query(
        default=None,
    ),
    end_date: (
        date | None
    ) = Query(
        default=None,
    ),
    knowledge_base_id: (
        UUID | None
    ) = Query(
        default=None,
    ),
    request_type: (
        str | None
    ) = Query(
        default=None,
        max_length=50,
    ),
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    tenant_id = (
        _require_tenant_id(
            current_user
        )
    )

    today = (
        datetime.now(
            timezone.utc
        ).date()
    )

    resolved_end_date = (
        end_date
        or today
    )

    resolved_start_date = (
        start_date
        or (
            resolved_end_date
            - timedelta(
                days=29
            )
        )
    )

    try:
        return (
            service.get_analytics(
                db=db,
                tenant_id=
                    tenant_id,
                start_date=
                    resolved_start_date,
                end_date=
                    resolved_end_date,
                knowledge_base_id=
                    knowledge_base_id,
                request_type=
                    request_type,
            )
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,
            detail=str(
                exc
            ),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,
            detail=str(
                exc
            ),
        ) from exc
