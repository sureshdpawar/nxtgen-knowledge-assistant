from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import (
    FileResponse,
)
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth.dependencies import (
    get_current_active_user,
)
from app.core.enums import (
    KnowledgeBaseAccessLevel,
)
from app.exceptions.document import (
    DocumentNotFoundError,
)
from app.exceptions.knowledge_source import (
    KnowledgeSourceNotFoundError,
)
from app.models.document import Document
from app.models.user import User
from app.schemas.document import (
    DocumentResponse,
)
from app.schemas.document_processing import (
    DocumentProcessingResponse,
)
from app.services.document_ingestion_service import (
    DocumentIngestionService,
)
from app.services.document_processing_service import (
    DocumentProcessingService,
)
from app.services.document_service import (
    DocumentService,
)
from app.services.knowledge_base_access_service import (
    KnowledgeBaseAccessService,
)
from app.services.knowledge_source_service import (
    KnowledgeSourceService,
)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


service = (
    DocumentIngestionService()
)

processing_service = (
    DocumentProcessingService()
)

document_service = (
    DocumentService()
)

access_service = (
    KnowledgeBaseAccessService()
)

knowledge_source_service = (
    KnowledgeSourceService()
)


def _require_document_access(
    *,
    db: Session,
    current_user: User,
    document_id: UUID,
    required_level:
        KnowledgeBaseAccessLevel =
        KnowledgeBaseAccessLevel.READ,
) -> Document:
    """
    Resolve a document and verify that the
    authenticated user has the required
    access level to the Knowledge Base
    that owns it.

    Security boundary:

    Document
      -> KnowledgeSource
      -> KnowledgeBase
      -> tenant
      -> user assignment
      -> access level

    The client does not provide tenant_id
    or knowledge_base_id for authorization.

    Ownership is derived from the persisted
    document itself.
    """

    document = (
        document_service.get_document(
            db=db,
            document_id=document_id,
        )
    )

    if document is None:
        raise DocumentNotFoundError()

    knowledge_base_id = (
        document_service
        .get_knowledge_base_id(
            db=db,
            document=document,
        )
    )

    access_service.require_access(
        db=db,
        current_user=current_user,
        knowledge_base_id=
            knowledge_base_id,
        required_level=
            required_level,
    )

    return document


def _require_knowledge_source_access(
    *,
    db: Session,
    current_user: User,
    knowledge_source_id: UUID,
    required_level:
        KnowledgeBaseAccessLevel =
        KnowledgeBaseAccessLevel.READ,
) -> UUID:
    """
    Resolve a Knowledge Source and verify
    that the authenticated user has the
    required access level to its owning
    Knowledge Base.

    Returns the resolved knowledge_base_id.

    KnowledgeSourceService.get() performs
    tenant validation.

    KnowledgeBaseAccessService then applies
    the user's KB-level permission.
    """

    knowledge_source = (
        knowledge_source_service.get(
            db=db,
            current_user=current_user,
            knowledge_source_id=
                knowledge_source_id,
        )
    )

    if knowledge_source is None:
        raise KnowledgeSourceNotFoundError()

    knowledge_base_id = (
        knowledge_source
        .knowledge_base_id
    )

    access_service.require_access(
        db=db,
        current_user=current_user,
        knowledge_base_id=
            knowledge_base_id,
        required_level=
            required_level,
    )

    return knowledge_base_id


@router.post(
    "/knowledge-source/"
    "{knowledge_source_id}",
    response_model=
        DocumentResponse,
    status_code=
        status.HTTP_201_CREATED,
)
def upload_document(
    knowledge_source_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        get_current_active_user,
    ),
):
    """
    Upload a document to a Knowledge Source.

    Requires MANAGE access because this
    operation modifies Knowledge Base
    content.
    """

    _require_knowledge_source_access(
        db=db,
        current_user=current_user,
        knowledge_source_id=
            knowledge_source_id,
        required_level=
            KnowledgeBaseAccessLevel.MANAGE,
    )

    return service.upload(
        db=db,
        current_user=current_user,
        knowledge_source_id=
            knowledge_source_id,
        file=file,
    )


@router.post(
    "/{document_id}/process",
    response_model=
        DocumentProcessingResponse,
)
def process_document(
    document_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        get_current_active_user,
    ),
):
    """
    Process or reprocess a document.

    Requires MANAGE access because processing
    changes persistent state, creates chunks
    and embeddings, and can invoke an
    embedding provider.
    """

    _require_document_access(
        db=db,
        current_user=current_user,
        document_id=document_id,
        required_level=
            KnowledgeBaseAccessLevel.MANAGE,
    )

    return (
        processing_service.process(
            db=db,
            document_id=document_id,
        )
    )


@router.get(
    "/knowledge-source/"
    "{knowledge_source_id}",
    response_model=
        list[DocumentResponse],
)
def list_documents(
    knowledge_source_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        get_current_active_user,
    ),
):
    """
    List documents belonging to a
    Knowledge Source.

    Requires READ access.

    MANAGE also satisfies READ.
    """

    _require_knowledge_source_access(
        db=db,
        current_user=current_user,
        knowledge_source_id=
            knowledge_source_id,
        required_level=
            KnowledgeBaseAccessLevel.READ,
    )

    return (
        document_service
        .list_by_knowledge_source(
            db=db,
            knowledge_source_id=
                knowledge_source_id,
        )
    )


@router.get(
    "/{document_id}/file",
)
def get_document_file(
    document_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        get_current_active_user,
    ),
):
    """
    Open/download the original document.

    Requires READ access.

    This is used by authenticated citation
    access in the application.
    """

    document = (
        _require_document_access(
            db=db,
            current_user=current_user,
            document_id=document_id,
            required_level=
                KnowledgeBaseAccessLevel.READ,
        )
    )

    file_path = (
        document_service
        .get_file_path(
            document,
        )
    )

    if not file_path.exists():
        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,
            detail=(
                "Document file "
                "not found."
            ),
        )

    return FileResponse(
        path=file_path,
        media_type=
            document.mime_type,
        filename=
            document.original_filename,
        content_disposition_type=
            "inline",
    )


@router.get(
    "/{document_id}",
    response_model=
        DocumentResponse,
)
def get_document(
    document_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        get_current_active_user,
    ),
):
    """
    Return document metadata.

    Requires READ access.

    Metadata is protected by the same
    Knowledge Base authorization boundary
    as the underlying file.
    """

    return (
        _require_document_access(
            db=db,
            current_user=current_user,
            document_id=document_id,
            required_level=
                KnowledgeBaseAccessLevel.READ,
        )
    )


@router.delete(
    "/{document_id}",
    status_code=
        status.HTTP_204_NO_CONTENT,
)
def delete_document(
    document_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        get_current_active_user,
    ),
):
    """
    Delete a document.

    Requires MANAGE access.

    Authorization is performed before
    deleting either the database record
    or physical source file.
    """

    _require_document_access(
        db=db,
        current_user=current_user,
        document_id=document_id,
        required_level=
            KnowledgeBaseAccessLevel.MANAGE,
    )

    deleted = (
        document_service
        .delete_document(
            db=db,
            document_id=document_id,
        )
    )

    if not deleted:
        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,
            detail=
                "Document not found",
        )

    return Response(
        status_code=
            status.HTTP_204_NO_CONTENT,
    )