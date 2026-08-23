from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
)


class PublicChannelChatRequest(
    BaseModel
):
    message: str = Field(
        min_length=1,
        max_length=10000,
    )

    session_id: UUID | None = None


class PublicChannelSource(
    BaseModel
):
    knowledge_source_id: UUID

    knowledge_source_name: str

    document_id: UUID

    document_name: str

    chunk_index: int

    page: int

    similarity: float


class PublicChannelChatResponse(
    BaseModel
):
    session_id: UUID

    answer: str

    sources: list[
        PublicChannelSource
    ]