from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.auth.permissions import (
    require_admin,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.tenant_llm_configuration import (
    CreateTenantLLMConfigurationRequest,
    KnowledgeBaseLLMConfigurationRequest,
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


service = (
    TenantLLMConfigurationService()
)


@router.get(
    "/profiles",
    response_model=list[
        TenantLLMConfigurationResponse
    ],
)
def list_profiles(
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    if current_user.tenant_id is None:
        return []

    return service.list_profiles(
        db=db,
        tenant_id=
            current_user.tenant_id,
    )


@router.post(
    "/profiles",
    response_model=
        TenantLLMConfigurationResponse,
    status_code=
        status.HTTP_201_CREATED,
)
def create_profile(
    payload:
        CreateTenantLLMConfigurationRequest,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    if current_user.tenant_id is None:
        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,
            detail=
                "Tenant is required.",
        )

    return service.create_profile(
        db=db,
        tenant_id=
            current_user.tenant_id,
        payload=payload,
    )


@router.get(
    "/profiles/{configuration_id}",
    response_model=
        TenantLLMConfigurationResponse,
)
def get_profile(
    configuration_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    if current_user.tenant_id is None:
        raise HTTPException(
            status_code=400,
            detail=
                "Tenant is required.",
        )

    try:
        return service.get_profile(
            db=db,
            tenant_id=
                current_user.tenant_id,
            configuration_id=
                configuration_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.put(
    "/profiles/{configuration_id}",
    response_model=
        TenantLLMConfigurationResponse,
)
def update_profile(
    configuration_id: UUID,
    payload:
        UpdateTenantLLMConfigurationRequest,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    if current_user.tenant_id is None:
        raise HTTPException(
            status_code=400,
            detail=
                "Tenant is required.",
        )

    try:
        return service.update_profile(
            db=db,
            tenant_id=
                current_user.tenant_id,
            configuration_id=
                configuration_id,
            payload=payload,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.put(
    "/profiles/{configuration_id}/default",
    response_model=
        TenantLLMConfigurationResponse,
)
def set_default_profile(
    configuration_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    if current_user.tenant_id is None:
        raise HTTPException(
            status_code=400,
            detail=
                "Tenant is required.",
        )

    try:
        return service.set_default(
            db=db,
            tenant_id=
                current_user.tenant_id,
            configuration_id=
                configuration_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.delete(
    "/profiles/{configuration_id}",
    status_code=
        status.HTTP_204_NO_CONTENT,
)
def delete_profile(
    configuration_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    if current_user.tenant_id is None:
        raise HTTPException(
            status_code=400,
            detail=
                "Tenant is required.",
        )

    try:
        service.delete_profile(
            db=db,
            tenant_id=
                current_user.tenant_id,
            configuration_id=
                configuration_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return Response(
        status_code=
            status.HTTP_204_NO_CONTENT,
    )


@router.put(
    "/knowledge-bases/{knowledge_base_id}",
)
def assign_profile_to_knowledge_base(
    knowledge_base_id: UUID,
    payload:
        KnowledgeBaseLLMConfigurationRequest,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    if current_user.tenant_id is None:
        raise HTTPException(
            status_code=400,
            detail=
                "Tenant is required.",
        )

    try:
        knowledge_base = (
            service
            .assign_to_knowledge_base(
                db=db,
                tenant_id=
                    current_user.tenant_id,
                knowledge_base_id=
                    knowledge_base_id,
                configuration_id=
                    payload
                    .llm_configuration_id,
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return {
        "knowledge_base_id":
            knowledge_base.id,

        "llm_configuration_id":
            knowledge_base
            .llm_configuration_id,
    }