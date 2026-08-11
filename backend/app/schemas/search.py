from uuid import UUID

from pydantic import BaseModel


class SearchRequest(BaseModel):
    knowledge_base_id: UUID
    query: str


class SearchResult(BaseModel):
    knowledge_source_id: UUID
    knowledge_source_name: str

    document_id: UUID
    document_name: str

    chunk_id: UUID
    chunk_index: int
    page: int

    similarity: float

    text: str


class SearchResponse(BaseModel):
    results: list[SearchResult]