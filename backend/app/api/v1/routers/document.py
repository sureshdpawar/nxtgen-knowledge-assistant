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
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth.dependencies import (
    get_current_active_user,
)
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

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

service = DocumentIngestionService()

processing_service = (
    DocumentProcessingService()
)

document_service = (
    DocumentService()
)


@router.post(
    "/knowledge-source/{knowledge_source_id}",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_document(
    knowledge_source_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_active_user,
    ),
):
    return service.upload(
        db=db,
        current_user=current_user,
        knowledge_source_id=knowledge_source_id,
        file=file,
    )


@router.post(
    "/{document_id}/process",
    response_model=DocumentProcessingResponse,
)
def process_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_active_user,
    ),
):
    return processing_service.process(
        db=db,
        document_id=document_id,
    )


@router.get(
    "/knowledge-source/{knowledge_source_id}",
    response_model=list[DocumentResponse],
)
def list_documents(
    knowledge_source_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_active_user,
    ),
):
    return (
        document_service
        .list_by_knowledge_source(
            db=db,
            knowledge_source_id=knowledge_source_id,
        )
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_active_user,
    ),
):
    document = (
        document_service.get_document(
            db=db,
            document_id=document_id,
        )
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return document


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_active_user,
    ),
):
    deleted = (
        document_service.delete_document(
            db=db,
            document_id=document_id,
        )
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return Response(
        status_code=
        status.HTTP_204_NO_CONTENT,
    )