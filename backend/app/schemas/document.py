from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.enums import DocumentStatus


class DocumentResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    knowledge_source_id: UUID

    uploaded_by: UUID

    original_filename: str

    stored_filename: str

    mime_type: str

    file_size: int

    checksum: str

    storage_path: str

    external_id: str | None

    status: DocumentStatus

    created_at: datetime

    updated_at: datetime