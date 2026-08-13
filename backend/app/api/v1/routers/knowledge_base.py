from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.auth.dependencies import (
    get_current_active_user,
)
from app.auth.permissions import (
    require_admin,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
    KnowledgeBaseUpdate,
)
from app.schemas.knowledge_base_access import (
    KnowledgeBaseAccessAssignRequest,
    KnowledgeBaseAccessResponse,
)
from app.services.knowledge_base_access_service import (
    KnowledgeBaseAccessService,
)
from app.services.knowledge_base_service import (
    KnowledgeBaseService,
)


router = APIRouter(
    prefix="/knowledge-bases",
    tags=["Knowledge Bases"],
)


service = KnowledgeBaseService()

access_service = (
    KnowledgeBaseAccessService()
)


@router.get(
    "/accessible",
    response_model=list[
        KnowledgeBaseResponse
    ],
)
def list_accessible_knowledge_bases(
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        get_current_active_user,
    ),
):
    return (
        access_service.list_accessible(
            db=db,
            current_user=current_user,
        )
    )


@router.get(
    "/",
    response_model=list[
        KnowledgeBaseResponse
    ],
)
def list_knowledge_bases(
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        get_current_active_user,
    ),
):
    return service.list(
        db,
        current_user,
    )


@router.get(
    "/{knowledge_base_id}",
    response_model=KnowledgeBaseResponse,
)
def get_knowledge_base(
    knowledge_base_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        get_current_active_user,
    ),
):
    return service.get(
        db,
        current_user,
        knowledge_base_id,
    )


@router.post(
    "/",
    response_model=KnowledgeBaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_knowledge_base(
    payload: KnowledgeBaseCreate,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    return service.create(
        db,
        current_user,
        payload,
    )


@router.put(
    "/{knowledge_base_id}",
    response_model=KnowledgeBaseResponse,
)
def update_knowledge_base(
    knowledge_base_id: UUID,
    payload: KnowledgeBaseUpdate,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    return service.update(
        db,
        current_user,
        knowledge_base_id,
        payload,
    )


@router.delete(
    "/{knowledge_base_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_knowledge_base(
    knowledge_base_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    service.delete(
        db,
        current_user,
        knowledge_base_id,
    )

    return Response(
        status_code=
            status.HTTP_204_NO_CONTENT,
    )


@router.post(
    "/{knowledge_base_id}/users/{user_id}",
    response_model=
        KnowledgeBaseAccessResponse,
)
def assign_user_to_knowledge_base(
    knowledge_base_id: UUID,
    user_id: UUID,
    payload:
        KnowledgeBaseAccessAssignRequest,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    return access_service.assign(
        db=db,
        current_user=current_user,
        user_id=user_id,
        knowledge_base_id=
            knowledge_base_id,
        access_level=
            payload.access_level,
    )


@router.delete(
    "/{knowledge_base_id}/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def revoke_user_from_knowledge_base(
    knowledge_base_id: UUID,
    user_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    access_service.revoke(
        db=db,
        current_user=current_user,
        user_id=user_id,
        knowledge_base_id=
            knowledge_base_id,
    )

    return Response(
        status_code=
            status.HTTP_204_NO_CONTENT,
    )