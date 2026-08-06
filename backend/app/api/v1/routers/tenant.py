from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.tenant import TenantCreate, TenantResponse
from app.services.tenant_service import TenantService
from uuid import UUID
from app.api.deps import get_tenant_service
from app.schemas.tenant import TenantUpdate
from fastapi import Response

router = APIRouter(
    prefix="/tenants",
    tags=["Tenants"],
)

service = TenantService()

@router.get("/", response_model=list[TenantResponse])
def list_tenants(
    db: Session = Depends(get_db),
    service: TenantService = Depends(get_tenant_service),
):
    return service.list(db)

@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant(
    tenant_id: UUID,
    db: Session = Depends(get_db),
):
    return service.get(db, tenant_id)

@router.post(
    "/",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_tenant(
    tenant: TenantCreate,
    db: Session = Depends(get_db),
):
    return service.create(db, tenant)
       
@router.put(
    "/{tenant_id}",
    response_model=TenantResponse,
)
def update_tenant(
    tenant_id: UUID,
    tenant: TenantUpdate,
    db: Session = Depends(get_db),
):
    return service.update(
        db,
        tenant_id,
        tenant,
    )      
        
@router.delete(
    "/{tenant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_tenant(
    tenant_id: UUID,
    db: Session = Depends(get_db),
):
    service.delete(
        db,
        tenant_id,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)