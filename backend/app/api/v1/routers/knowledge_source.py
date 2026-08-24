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
from app.core.enums import (
    KnowledgeBaseAccessLevel,
)
from app.models.knowledge_source import (
    KnowledgeSource,
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
from app.services.knowledge_base_access_service import (
    KnowledgeBaseAccessService,
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

access_service = (
    KnowledgeBaseAccessService()
)


def _require_knowledge_base_access(
    *,
    db: Session,
    current_user: User,
    knowledge_base_id: UUID,
    required_level:
        KnowledgeBaseAccessLevel,
) -> None:
    """
    Verify access to an explicitly identified
    Knowledge Base.

    The KnowledgeBaseAccessService also checks
    the tenant boundary.
    """

    access_service.require_access(
        db=db,
        current_user=current_user,
        knowledge_base_id=
            knowledge_base_id,
        required_level=
            required_level,
    )


def _require_knowledge_source_access(
    *,
    db: Session,
    current_user: User,
    knowledge_source_id: UUID,
    required_level:
        KnowledgeBaseAccessLevel,
) -> KnowledgeSource:
    """
    Resolve a Knowledge Source using the
    tenant-aware service and then enforce
    READ or MANAGE access against its owning
    Knowledge Base.

    Security chain:

        KnowledgeSource
              ↓
        KnowledgeBase
              ↓
           Tenant
              ↓
        User assignment
              ↓
        READ / MANAGE
    """

    knowledge_source = (
        service.get(
            db=db,
            current_user=
                current_user,
            knowledge_source_id=
                knowledge_source_id,
        )
    )

    access_service.require_access(
        db=db,
        current_user=current_user,
        knowledge_base_id=
            knowledge_source
            .knowledge_base_id,
        required_level=
            required_level,
    )

    return knowledge_source


@router.post(
    "/knowledge-base/"
    "{knowledge_base_id}",
    response_model=
        KnowledgeSourceResponse,
    status_code=
        status.HTTP_201_CREATED,
)
def create_knowledge_source(
    knowledge_base_id: UUID,
    payload:
        KnowledgeSourceCreate,
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_active_user
    ),
):
    """
    Create a Knowledge Source.

    Requires MANAGE access because this
    changes the contents/configuration of
    the Knowledge Base.
    """

    _require_knowledge_base_access(
        db=db,
        current_user=current_user,
        knowledge_base_id=
            knowledge_base_id,
        required_level=
            KnowledgeBaseAccessLevel.MANAGE,
    )

    return service.create(
        db,
        current_user,
        knowledge_base_id,
        payload,
    )


@router.get(
    "/knowledge-base/"
    "{knowledge_base_id}",
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
    """
    List Knowledge Sources.

    Requires READ access.

    MANAGE implicitly satisfies READ.
    """

    _require_knowledge_base_access(
        db=db,
        current_user=current_user,
        knowledge_base_id=
            knowledge_base_id,
        required_level=
            KnowledgeBaseAccessLevel.READ,
    )

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
    """
    Trigger a Knowledge Source sync.

    Requires MANAGE access.

    A sync is a mutating operation because
    it can:

    - create documents
    - replace document content
    - delete missing documents
    - create chunks/embeddings
    - invoke external providers
    """

    _require_knowledge_source_access(
        db=db,
        current_user=current_user,
        knowledge_source_id=
            knowledge_source_id,
        required_level=
            KnowledgeBaseAccessLevel.MANAGE,
    )

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
    """
    View Knowledge Source sync history.

    Requires READ access because this is
    diagnostic/read-only information.
    """

    _require_knowledge_source_access(
        db=db,
        current_user=current_user,
        knowledge_source_id=
            knowledge_source_id,
        required_level=
            KnowledgeBaseAccessLevel.READ,
    )

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
    """
    Return Knowledge Source metadata.

    Requires READ access.
    """

    return (
        _require_knowledge_source_access(
            db=db,
            current_user=
                current_user,
            knowledge_source_id=
                knowledge_source_id,
            required_level=
                KnowledgeBaseAccessLevel.READ,
        )
    )


@router.put(
    "/{knowledge_source_id}",
    response_model=(
        KnowledgeSourceResponse
    ),
)
def update_knowledge_source(
    knowledge_source_id: UUID,
    payload:
        KnowledgeSourceUpdate,
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_active_user
    ),
):
    """
    Update Knowledge Source configuration.

    Requires MANAGE access.
    """

    _require_knowledge_source_access(
        db=db,
        current_user=current_user,
        knowledge_source_id=
            knowledge_source_id,
        required_level=
            KnowledgeBaseAccessLevel.MANAGE,
    )

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
    """
    Delete a Knowledge Source.

    Requires MANAGE access.

    This is particularly sensitive because
    deleting a Knowledge Source may remove
    its associated document hierarchy.
    """

    _require_knowledge_source_access(
        db=db,
        current_user=current_user,
        knowledge_source_id=
            knowledge_source_id,
        required_level=
            KnowledgeBaseAccessLevel.MANAGE,
    )

    service.delete(
        db,
        current_user,
        knowledge_source_id,
    )