from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from app.auth.permissions import (
    require_admin,
    require_superadmin,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard import (
    DashboardStatsResponse,
    PlatformDashboardStatsResponse,
)
from app.services.dashboard_service import (
    DashboardService,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


service = DashboardService()


@router.get(
    "/stats",
    response_model=
        DashboardStatsResponse,
)
def get_dashboard_stats(
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    return (
        service.get_admin_stats(
            db=db,
            current_user=current_user,
        )
    )


@router.get(
    "/platform-stats",
    response_model=
        PlatformDashboardStatsResponse,
)
def get_platform_dashboard_stats(
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_superadmin,
    ),
):
    return (
        service.get_platform_stats(
            db=db,
        )
    )