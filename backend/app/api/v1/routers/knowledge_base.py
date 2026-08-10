from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.auth.permissions import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
    KnowledgeBaseUpdate,
)
from app.services.knowledge_base_service import KnowledgeBaseService

router = APIRouter(
    prefix="/knowledge-bases",
    tags=["Knowledge Bases"],
)

service = KnowledgeBaseService()


@router.get(
    "/",
    response_model=list[KnowledgeBaseResponse],
)
def list_knowledge_bases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
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
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
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
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
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
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service.delete(
        db,
        current_user,
        knowledge_base_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )