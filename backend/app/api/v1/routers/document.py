from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.services.document_ingestion_service import (
    DocumentIngestionService,
)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

service = DocumentIngestionService()


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