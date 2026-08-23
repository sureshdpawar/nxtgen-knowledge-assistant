from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
)


class WebsiteSessionRequest(
    BaseModel
):
    channel_id: UUID


class WebsiteSessionResponse(
    BaseModel
):
    token: str

    expires_in: int

    visitor_id: str


class WebsiteChatRequest(
    BaseModel
):
    message: str = Field(
        min_length=1,
        max_length=10000,
    )

    session_id: UUID | None = None


class WebsiteWidgetConfigResponse(
    BaseModel
):
    channel_id: UUID

    name: str

    widget_title: str

    welcome_message: str

    placeholder: str

    show_sources: bool