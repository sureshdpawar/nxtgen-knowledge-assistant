from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.auth.permissions import (
    require_admin,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.integration import (
    IntegrationCreate,
    IntegrationResponse,
    IntegrationUpdate,
)
from app.services.integration_service import (
    IntegrationService,
)


router = APIRouter(
    prefix="/integrations",
    tags=["Integrations"],
)


service = IntegrationService()


@router.get(
    "",
    response_model=list[
        IntegrationResponse
    ],
)
def list_integrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_admin,
    ),
):
    return service.list(
        db=db,
        current_user=current_user,
    )


@router.post(
    "",
    response_model=
        IntegrationResponse,
    status_code=
        status.HTTP_201_CREATED,
)
def create_integration(
    payload: IntegrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_admin,
    ),
):
    return service.create(
        db=db,
        current_user=current_user,
        payload=payload,
    )


@router.get(
    "/{integration_id}",
    response_model=
        IntegrationResponse,
)
def get_integration(
    integration_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_admin,
    ),
):
    return service.get(
        db=db,
        current_user=current_user,
        integration_id=
            integration_id,
    )


@router.put(
    "/{integration_id}",
    response_model=
        IntegrationResponse,
)
def update_integration(
    integration_id: UUID,
    payload: IntegrationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_admin,
    ),
):
    return service.update(
        db=db,
        current_user=current_user,
        integration_id=
            integration_id,
        payload=payload,
    )


@router.delete(
    "/{integration_id}",
    status_code=
        status.HTTP_204_NO_CONTENT,
)
def delete_integration(
    integration_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_admin,
    ),
):
    service.delete(
        db=db,
        current_user=current_user,
        integration_id=
            integration_id,
    )

    return Response(
        status_code=
            status.HTTP_204_NO_CONTENT,
    )