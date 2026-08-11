from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth.dependencies import (
    get_current_active_user,
)
from app.models.user import User
from app.schemas.tenant_llm_configuration import (
    TenantLLMConfigurationResponse,
    UpdateTenantLLMConfigurationRequest,
)
from app.services.tenant_llm_configuration_service import (
    TenantLLMConfigurationService,
)

router = APIRouter(
    prefix="/llm-config",
    tags=["LLM Configuration"],
)

service = TenantLLMConfigurationService()


@router.get(
    "",
    response_model=TenantLLMConfigurationResponse,
)
def get_configuration(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_active_user,
    ),
):

    configuration = service.get_active_configuration(
        db=db,
        tenant_id=current_user.tenant_id,
    )

    if configuration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM configuration not found.",
        )

    return configuration


@router.put(
    "",
    response_model=TenantLLMConfigurationResponse,
)
def update_configuration(
    payload: UpdateTenantLLMConfigurationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_active_user,
    ),
):

    configuration = service.update_configuration(
        db=db,
        tenant_id=current_user.tenant_id,
        payload=payload,
    )

    return configuration