from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
)


class ConversationSummary(
    BaseModel
):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    knowledge_base_id: UUID

    title: str

    created_at: datetime

    updated_at: datetime


class ChannelConversationSummary(
    BaseModel
):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    knowledge_base_id: UUID

    chat_channel_id: UUID

    title: str

    created_at: datetime

    updated_at: datetime


class ConversationMessageResponse(
    BaseModel
):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    role: str

    content: str

    citations: list

    token_usage: dict

    created_at: datetime


class ConversationResponse(
    BaseModel
):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    knowledge_base_id: UUID

    title: str

    created_at: datetime

    updated_at: datetime

    messages: list[
        ConversationMessageResponse
    ]


class ChannelConversationResponse(
    BaseModel
):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    knowledge_base_id: UUID

    chat_channel_id: UUID

    title: str

    created_at: datetime

    updated_at: datetime

    messages: list[
        ConversationMessageResponse
    ]


class ConversationListResponse(
    BaseModel
):
    conversations: list[
        ConversationSummary
    ]


class ChannelConversationListResponse(
    BaseModel
):
    conversations: list[
        ChannelConversationSummary
    ]