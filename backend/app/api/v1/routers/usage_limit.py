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
from app.schemas.usage_limit import (
    UsageLimitCreate,
    UsageLimitResponse,
    UsageLimitUpdate,
)
from app.schemas.usage_status import (
    UsageStatusResponse,
)
from app.services.usage_limit_service import (
    UsageLimitService,
)
from app.services.usage_status_service import (
    UsageStatusService,
)


router = APIRouter(
    prefix="/usage-limits",
    tags=["Usage Limits"],
)


service = (
    UsageLimitService()
)

status_service = (
    UsageStatusService()
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


#
# Tenant-level quota
#


@router.get(
    "/tenant",
    response_model=
        UsageLimitResponse | None,
)
def get_tenant_limit(
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

    return (
        service.get_tenant_limit(
            db=db,
            tenant_id=
                tenant_id,
        )
    )


@router.put(
    "/tenant",
    response_model=
        UsageLimitResponse,
)
def upsert_tenant_limit(
    payload: UsageLimitUpdate,
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

    existing = (
        service.get_tenant_limit(
            db=db,
            tenant_id=
                tenant_id,
        )
    )

    try:
        if existing is None:
            create_payload = (
                UsageLimitCreate(
                    tenant_id=
                        tenant_id,
                    **payload.model_dump(
                        exclude_unset=True,
                    ),
                )
            )

            return service.create(
                db=db,
                payload=
                    create_payload,
            )

        return service.update(
            db=db,
            usage_limit_id=
                existing.id,
            payload=
                payload,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,
            detail=str(
                exc
            ),
        ) from exc


#
# Knowledge Base quota
#


@router.get(
    "/knowledge-bases/"
    "{knowledge_base_id}",
    response_model=
        UsageLimitResponse | None,
)
def get_knowledge_base_limit(
    knowledge_base_id: UUID,
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

    usage_limit = (
        service
        .get_knowledge_base_limit(
            db=db,
            knowledge_base_id=
                knowledge_base_id,
        )
    )

    if (
        usage_limit is not None
        and usage_limit.tenant_id
        != tenant_id
    ):
        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,
            detail=(
                "Usage limit not found."
            ),
        )

    return usage_limit


@router.put(
    "/knowledge-bases/"
    "{knowledge_base_id}",
    response_model=
        UsageLimitResponse,
)
def upsert_knowledge_base_limit(
    knowledge_base_id: UUID,
    payload: UsageLimitUpdate,
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

    existing = (
        service
        .get_knowledge_base_limit(
            db=db,
            knowledge_base_id=
                knowledge_base_id,
        )
    )

    if (
        existing is not None
        and existing.tenant_id
        != tenant_id
    ):
        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,
            detail=(
                "Usage limit not found."
            ),
        )

    try:
        if existing is None:
            create_payload = (
                UsageLimitCreate(
                    tenant_id=
                        tenant_id,
                    knowledge_base_id=
                        knowledge_base_id,
                    **payload.model_dump(
                        exclude_unset=True,
                    ),
                )
            )

            return service.create(
                db=db,
                payload=
                    create_payload,
            )

        return service.update(
            db=db,
            usage_limit_id=
                existing.id,
            payload=
                payload,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,
            detail=str(
                exc
            ),
        ) from exc


#
# Chat Channel quota
#


@router.get(
    "/chat-channels/"
    "{chat_channel_id}",
    response_model=
        UsageLimitResponse | None,
)
def get_chat_channel_limit(
    chat_channel_id: UUID,
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

    usage_limit = (
        service
        .get_chat_channel_limit(
            db=db,
            chat_channel_id=
                chat_channel_id,
        )
    )

    if (
        usage_limit is not None
        and usage_limit.tenant_id
        != tenant_id
    ):
        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,
            detail=(
                "Usage limit not found."
            ),
        )

    return usage_limit


@router.put(
    "/chat-channels/"
    "{chat_channel_id}/"
    "knowledge-bases/"
    "{knowledge_base_id}",
    response_model=
        UsageLimitResponse,
)
def upsert_chat_channel_limit(
    chat_channel_id: UUID,
    knowledge_base_id: UUID,
    payload: UsageLimitUpdate,
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

    existing = (
        service
        .get_chat_channel_limit(
            db=db,
            chat_channel_id=
                chat_channel_id,
        )
    )

    if (
        existing is not None
        and existing.tenant_id
        != tenant_id
    ):
        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,
            detail=(
                "Usage limit not found."
            ),
        )

    try:
        if existing is None:
            create_payload = (
                UsageLimitCreate(
                    tenant_id=
                        tenant_id,
                    knowledge_base_id=
                        knowledge_base_id,
                    chat_channel_id=
                        chat_channel_id,
                    **payload.model_dump(
                        exclude_unset=True,
                    ),
                )
            )

            return service.create(
                db=db,
                payload=
                    create_payload,
            )

        return service.update(
            db=db,
            usage_limit_id=
                existing.id,
            payload=
                payload,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,
            detail=str(
                exc
            ),
        ) from exc


#
# Usage status
#


@router.get(
    "/status/tenant",
    response_model=
        UsageStatusResponse,
)
def get_tenant_usage_status(
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

    return (
        status_service.get_status(
            db=db,
            tenant_id=
                tenant_id,
        )
    )


@router.get(
    "/status/knowledge-bases/"
    "{knowledge_base_id}",
    response_model=
        UsageStatusResponse,
)
def get_knowledge_base_usage_status(
    knowledge_base_id: UUID,
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

    usage_limit = (
        service
        .get_knowledge_base_limit(
            db=db,
            knowledge_base_id=
                knowledge_base_id,
        )
    )

    if (
        usage_limit is not None
        and usage_limit.tenant_id
        != tenant_id
    ):
        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,
            detail=(
                "Usage limit not found."
            ),
        )

    return (
        status_service.get_status(
            db=db,
            tenant_id=
                tenant_id,
            knowledge_base_id=
                knowledge_base_id,
        )
    )


@router.get(
    "/status/chat-channels/"
    "{chat_channel_id}/"
    "knowledge-bases/"
    "{knowledge_base_id}",
    response_model=
        UsageStatusResponse,
)
def get_chat_channel_usage_status(
    chat_channel_id: UUID,
    knowledge_base_id: UUID,
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

    usage_limit = (
        service
        .get_chat_channel_limit(
            db=db,
            chat_channel_id=
                chat_channel_id,
        )
    )

    if (
        usage_limit is not None
        and usage_limit.tenant_id
        != tenant_id
    ):
        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,
            detail=(
                "Usage limit not found."
            ),
        )

    return (
        status_service.get_status(
            db=db,
            tenant_id=
                tenant_id,
            knowledge_base_id=
                knowledge_base_id,
            chat_channel_id=
                chat_channel_id,
        )
    )


#
# Delete quota configuration
#
# Deleting means there is no configured
# quota at this scope.
#


@router.delete(
    "/{usage_limit_id}",
    status_code=
        status.HTTP_204_NO_CONTENT,
)
def delete_usage_limit(
    usage_limit_id: UUID,
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

    usage_limit = (
        service.get(
            db=db,
            usage_limit_id=
                usage_limit_id,
        )
    )

    if (
        usage_limit is None
        or usage_limit.tenant_id
        != tenant_id
    ):
        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,
            detail=(
                "Usage limit not found."
            ),
        )

    try:
        service.delete(
            db=db,
            usage_limit_id=
                usage_limit_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,
            detail=str(
                exc
            ),
        ) from exc

    return Response(
        status_code=
            status.HTTP_204_NO_CONTENT,
    )