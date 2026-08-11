from uuid import UUID

from pydantic import BaseModel


class ChatRequest(BaseModel):
    knowledge_base_id: UUID
    query: str


class ChatResponse(BaseModel):
    answer: str