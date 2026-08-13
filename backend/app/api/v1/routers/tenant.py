from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.auth.permissions import (
    require_superadmin,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.tenant import (
    TenantCreate,
    TenantResponse,
    TenantUpdate,
)
from app.schemas.user import (
    TenantAdminCreate,
    UserResponse,
)
from app.services.tenant_service import (
    TenantService,
)
from app.services.user_service import (
    UserService,
)


router = APIRouter(
    prefix="/tenants",
    tags=["Tenants"],
)


service = TenantService()

user_service = UserService()


@router.get(
    "/",
    response_model=list[
        TenantResponse
    ],
)
def list_tenants(
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_superadmin,
    ),
):
    return service.list(
        db,
    )


@router.get(
    "/{tenant_id}",
    response_model=
        TenantResponse,
)
def get_tenant(
    tenant_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_superadmin,
    ),
):
    return service.get(
        db,
        tenant_id,
    )


@router.post(
    "/",
    response_model=
        TenantResponse,
    status_code=
        status.HTTP_201_CREATED,
)
def create_tenant(
    tenant: TenantCreate,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_superadmin,
    ),
):
    return service.create(
        db,
        tenant,
    )


@router.put(
    "/{tenant_id}",
    response_model=
        TenantResponse,
)
def update_tenant(
    tenant_id: UUID,
    tenant: TenantUpdate,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_superadmin,
    ),
):
    return service.update(
        db,
        tenant_id,
        tenant,
    )


@router.post(
    "/{tenant_id}/admins",
    response_model=
        UserResponse,
    status_code=
        status.HTTP_201_CREATED,
)
def create_tenant_admin(
    tenant_id: UUID,
    admin:
        TenantAdminCreate,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_superadmin,
    ),
):
    return (
        user_service
        .create_tenant_admin(
            db=db,
            tenant_id=tenant_id,
            admin_create=admin,
        )
    )


@router.delete(
    "/{tenant_id}",
    status_code=
        status.HTTP_204_NO_CONTENT,
)
def delete_tenant(
    tenant_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_superadmin,
    ),
):
    service.delete(
        db,
        tenant_id,
    )

    return Response(
        status_code=
            status.HTTP_204_NO_CONTENT,
    )