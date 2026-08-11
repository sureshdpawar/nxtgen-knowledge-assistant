from uuid import UUID

from pydantic import BaseModel


class DocumentProcessingResponse(BaseModel):
    document_id: UUID
    chunks_created: int