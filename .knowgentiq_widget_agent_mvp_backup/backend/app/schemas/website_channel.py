from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class WebsitePreChatField(BaseModel):
    name: str
    label: str
    required: bool = False
    input_type: Literal["text", "tel", "email"] = "text"
    placeholder: str | None = None


class WebsitePreChatConfig(BaseModel):
    enabled: bool = False
    title: str = "Before we start"
    submit_label: str = "Start chat"
    fields: list[WebsitePreChatField] = Field(default_factory=list)


class WebsiteSessionRequest(BaseModel):
    channel_id: UUID
    visitor: dict[str, str] = Field(default_factory=dict)


class WebsiteSessionResponse(BaseModel):
    token: str
    expires_in: int
    visitor_id: str
    thread_id: UUID


class WebsiteChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10000)
    session_id: UUID | None = None


class WebsiteWidgetConfigResponse(BaseModel):
    channel_id: UUID
    name: str
    widget_title: str
    welcome_message: str
    placeholder: str
    show_sources: bool
    execution_mode: Literal["KNOWLEDGE", "AGENT"]
    pre_chat: WebsitePreChatConfig
