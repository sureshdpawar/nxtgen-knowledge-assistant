from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ConversationSummary(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationMessageResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    role: str
    content: str
    citations: list
    token_usage: dict
    created_at: datetime


class ConversationResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[ConversationMessageResponse]


class ConversationListResponse(BaseModel):
    conversations: list[ConversationSummary]