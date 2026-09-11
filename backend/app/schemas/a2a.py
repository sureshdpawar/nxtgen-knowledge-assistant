from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class A2APart(BaseModel):
    text: str | None = None
    data: Any | None = None
    media_type: str | None = Field(
        default=None,
        alias="mediaType",
    )

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }


class A2AMessage(BaseModel):
    message_id: str = Field(alias="messageId")
    context_id: str | None = Field(
        default=None,
        alias="contextId",
    )
    task_id: str | None = Field(
        default=None,
        alias="taskId",
    )
    role: Literal[
        "ROLE_USER",
        "ROLE_AGENT",
    ]
    parts: list[A2APart]
    metadata: dict[str, Any] | None = None

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }


class A2ASendMessageRequest(BaseModel):
    tenant: str | None = None
    message: A2AMessage
    configuration: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


class A2ASendMessageResponse(BaseModel):
    message: A2AMessage
