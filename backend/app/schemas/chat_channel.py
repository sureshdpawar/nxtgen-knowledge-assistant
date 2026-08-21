from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.core.enums import (
    ChatChannelStatus,
    ChatChannelType,
)


class ChatChannelCreate(
    BaseModel
):
    knowledge_base_id: UUID

    name: str = Field(
        min_length=2,
        max_length=150,
    )

    type: ChatChannelType

    configuration: dict = Field(
        default_factory=dict,
    )


class ChatChannelUpdate(
    BaseModel
):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    status: (
        ChatChannelStatus
        | None
    ) = None

    configuration: (
        dict
        | None
    ) = None


class ChatChannelResponse(
    BaseModel
):
    id: UUID

    tenant_id: UUID

    knowledge_base_id: UUID

    name: str

    type: ChatChannelType

    status: ChatChannelStatus

    configuration: dict

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class ChatChannelApiKeyCreate(
    BaseModel
):
    name: str = Field(
        min_length=2,
        max_length=150,
    )


class ChatChannelApiKeyCreatedResponse(
    BaseModel
):
    id: UUID

    name: str

    key_prefix: str

    api_key: str


class ChatChannelApiKeyResponse(
    BaseModel
):
    id: UUID

    name: str

    key_prefix: str

    active: bool

    last_used_at: datetime | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )