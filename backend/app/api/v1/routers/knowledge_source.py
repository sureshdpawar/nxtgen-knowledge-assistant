from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth.dependencies import (
    get_current_active_user,
)
from app.models.user import User
from app.schemas.knowledge_source import (
    KnowledgeSourceCreate,
    KnowledgeSourceResponse,
    KnowledgeSourceUpdate,
)
from app.schemas.knowledge_source_sync import (
    KnowledgeSourceSyncResponse,
)
from app.services.knowledge_source_service import (
    KnowledgeSourceService,
)
from app.services.knowledge_source_sync_service import (
    KnowledgeSourceSyncService,
)


router = APIRouter(
    prefix="/knowledge-sources",
    tags=["Knowledge Sources"],
)


service = (
    KnowledgeSourceService()
)

sync_service = (
    KnowledgeSourceSyncService()
)


@router.post(
    "/knowledge-base/{knowledge_base_id}",
    response_model=KnowledgeSourceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_knowledge_source(
    knowledge_base_id: UUID,
    payload: KnowledgeSourceCreate,
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_active_user
    ),
):
    return service.create(
        db,
        current_user,
        knowledge_base_id,
        payload,
    )


@router.get(
    "/knowledge-base/{knowledge_base_id}",
    response_model=(
        list[
            KnowledgeSourceResponse
        ]
    ),
)
def list_knowledge_sources(
    knowledge_base_id: UUID,
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_active_user
    ),
):
    return service.list(
        db,
        current_user,
        knowledge_base_id,
    )


@router.post(
    "/{knowledge_source_id}/sync",
    response_model=(
        KnowledgeSourceSyncResponse
    ),
)
def sync_knowledge_source(
    knowledge_source_id: UUID,
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_active_user
    ),
):
    return sync_service.sync(
        db=db,
        current_user=current_user,
        knowledge_source_id=(
            knowledge_source_id
        ),
    )


@router.get(
    "/{knowledge_source_id}/syncs",
    response_model=(
        list[
            KnowledgeSourceSyncResponse
        ]
    ),
)
def list_knowledge_source_syncs(
    knowledge_source_id: UUID,
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_active_user
    ),
):
    return sync_service.list_syncs(
        db=db,
        current_user=current_user,
        knowledge_source_id=(
            knowledge_source_id
        ),
    )


@router.get(
    "/{knowledge_source_id}",
    response_model=(
        KnowledgeSourceResponse
    ),
)
def get_knowledge_source(
    knowledge_source_id: UUID,
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_active_user
    ),
):
    return service.get(
        db,
        current_user,
        knowledge_source_id,
    )


@router.put(
    "/{knowledge_source_id}",
    response_model=(
        KnowledgeSourceResponse
    ),
)
def update_knowledge_source(
    knowledge_source_id: UUID,
    payload: KnowledgeSourceUpdate,
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_active_user
    ),
):
    return service.update(
        db,
        current_user,
        knowledge_source_id,
        payload,
    )


@router.delete(
    "/{knowledge_source_id}",
    status_code=(
        status.HTTP_204_NO_CONTENT
    ),
)
def delete_knowledge_source(
    knowledge_source_id: UUID,
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_active_user
    ),
):
    service.delete(
        db,
        current_user,
        knowledge_source_id,
    )