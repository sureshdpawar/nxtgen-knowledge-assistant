from uuid import UUID

from sqlalchemy.orm import Session

from app.models.chat_channel_slack_conversation import (
    ChatChannelSlackConversation,
)
from app.repositories.chat_channel_slack_conversation_repository import (
    ChatChannelSlackConversationRepository,
)


class SlackConversationService:

    def __init__(self):
        self.repository = (
            ChatChannelSlackConversationRepository()
        )

    def get_conversation_id(
        self,
        db: Session,
        channel_id: UUID,
        slack_team_id: str,
        slack_channel_id: str,
        slack_thread_ts: str,
    ) -> UUID | None:
        mapping = (
            self.repository
            .get_by_thread(
                db=db,
                channel_id=channel_id,
                slack_team_id=(
                    slack_team_id
                ),
                slack_channel_id=(
                    slack_channel_id
                ),
                slack_thread_ts=(
                    slack_thread_ts
                ),
            )
        )

        if mapping is None:
            return None

        return (
            mapping
            .conversation_id
        )

    def create_mapping(
        self,
        db: Session,
        channel_id: UUID,
        conversation_id: UUID,
        slack_team_id: str,
        slack_channel_id: str,
        slack_thread_ts: str,
        slack_user_id:
            str | None,
    ) -> (
        ChatChannelSlackConversation
    ):
        existing = (
            self.repository
            .get_by_thread(
                db=db,
                channel_id=channel_id,
                slack_team_id=(
                    slack_team_id
                ),
                slack_channel_id=(
                    slack_channel_id
                ),
                slack_thread_ts=(
                    slack_thread_ts
                ),
            )
        )

        if existing is not None:
            return existing

        mapping = (
            ChatChannelSlackConversation(
                channel_id=(
                    channel_id
                ),
                conversation_id=(
                    conversation_id
                ),
                slack_team_id=(
                    slack_team_id
                ),
                slack_channel_id=(
                    slack_channel_id
                ),
                slack_thread_ts=(
                    slack_thread_ts
                ),
                slack_user_id=(
                    slack_user_id
                ),
            )
        )

        self.repository.create(
            db,
            mapping,
        )

        db.commit()

        db.refresh(
            mapping
        )

        return mapping