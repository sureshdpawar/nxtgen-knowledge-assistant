from uuid import UUID

from pydantic import BaseModel


class ChatRequest(BaseModel):
    knowledge_base_id: UUID
    conversation_id: UUID | None = None
    query: str


class ChatCitation(BaseModel):
    knowledge_source_id: UUID
    knowledge_source_name: str

    document_id: UUID
    document_name: str

    chunk_index: int
    page: int
    similarity: float


class ChatResponse(BaseModel):
    conversation_id: UUID
    answer: str
    sources: list[ChatCitation]