from uuid import UUID

from sqlalchemy import (
    select,
)
from sqlalchemy.orm import (
    Session,
)

from app.models.chat_channel_slack_conversation import (
    ChatChannelSlackConversation,
)
from app.repositories.base_repository import (
    BaseRepository,
)


class ChatChannelSlackConversationRepository(
    BaseRepository[
        ChatChannelSlackConversation
    ]
):

    def __init__(self):
        super().__init__(
            ChatChannelSlackConversation
        )

    def get_by_thread(
        self,
        db: Session,
        channel_id: UUID,
        slack_team_id: str,
        slack_channel_id: str,
        slack_thread_ts: str,
    ) -> (
        ChatChannelSlackConversation
        | None
    ):
        stmt = (
            select(
                ChatChannelSlackConversation
            )
            .where(
                ChatChannelSlackConversation
                .channel_id
                == channel_id,

                ChatChannelSlackConversation
                .slack_team_id
                == slack_team_id,

                ChatChannelSlackConversation
                .slack_channel_id
                == slack_channel_id,

                ChatChannelSlackConversation
                .slack_thread_ts
                == slack_thread_ts,
            )
        )

        return (
            db.execute(
                stmt
            )
            .scalars()
            .first()
        )

    def get_by_conversation_id(
        self,
        db: Session,
        conversation_id: UUID,
    ) -> (
        ChatChannelSlackConversation
        | None
    ):
        stmt = (
            select(
                ChatChannelSlackConversation
            )
            .where(
                ChatChannelSlackConversation
                .conversation_id
                == conversation_id
            )
        )

        return (
            db.execute(
                stmt
            )
            .scalars()
            .first()
        )