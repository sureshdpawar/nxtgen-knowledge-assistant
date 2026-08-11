from uuid import UUID

from pydantic import BaseModel


class ChatRequest(BaseModel):
    knowledge_base_id: UUID
    query: str


class ChatCitation(BaseModel):
    knowledge_source_name: str
    document_name: str
    chunk_index: int
    page: int
    similarity: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatCitation]