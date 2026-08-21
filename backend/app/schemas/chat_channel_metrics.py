from datetime import datetime

from pydantic import BaseModel


class ChatChannelMetricsResponse(
    BaseModel
):
    conversation_count: int

    message_count: int

    user_message_count: int

    assistant_message_count: int

    last_activity_at:datetime | None

    active_api_key_count: int

    revoked_api_key_count: int