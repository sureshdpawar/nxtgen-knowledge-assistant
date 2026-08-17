from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from app.auth.dependencies import (
    get_current_active_user,
)
from app.db.session import get_db
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
)
from app.schemas.user import (
    UserResponse,
)
from app.services.auth_service import (
    AuthService,
)


router = APIRouter(
    prefix="/auth",
    tags=[
        "Authentication",
    ],
)


service = AuthService()


@router.post(
    "/login",
    response_model=
        TokenResponse,
)
def login(
    login_request:
        LoginRequest,
    db: Session = Depends(
        get_db,
    ),
):
    return service.login(
        db,
        login_request,
    )


@router.get(
    "/me",
    response_model=
        UserResponse,
)
def me(
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        get_current_active_user,
    ),
):
    tenant_name = None

    if (
        current_user.tenant_id
        is not None
    ):
        tenant = db.get(
            Tenant,
            current_user.tenant_id,
        )

        if tenant is not None:
            tenant_name = (
                tenant.name
            )

    return {
        "id":
            current_user.id,

        "tenant_id":
            current_user.tenant_id,

        "tenant_name":
            tenant_name,

        "first_name":
            current_user.first_name,

        "last_name":
            current_user.last_name,

        "email":
            current_user.email,

        "role":
            current_user.role,

        "is_active":
            current_user.is_active,

        "created_at":
            current_user.created_at,

        "updated_at":
            current_user.updated_at,
    }