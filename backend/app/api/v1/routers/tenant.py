from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.tenant import TenantCreate, TenantResponse
from app.services.tenant_service import TenantService

router = APIRouter(
    prefix="/tenants",
    tags=["Tenants"],
)

service = TenantService()


@router.post(
    "/",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_tenant(
    tenant: TenantCreate,
    db: Session = Depends(get_db),
):

    try:
        return service.create(db, tenant)

    except ValueError as ex:
        raise HTTPException(
            status_code=400,
            detail=str(ex),
        )