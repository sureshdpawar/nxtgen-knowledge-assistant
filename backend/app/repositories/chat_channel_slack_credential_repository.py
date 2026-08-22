from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chat_channel_slack_credential import (
    ChatChannelSlackCredential,
)
from app.repositories.base_repository import (
    BaseRepository,
)


class ChatChannelSlackCredentialRepository(
    BaseRepository[
        ChatChannelSlackCredential
    ]
):

    def __init__(self):
        super().__init__(
            ChatChannelSlackCredential
        )

    def get_by_channel(
        self,
        db: Session,
        channel_id: UUID,
    ) -> (
        ChatChannelSlackCredential
        | None
    ):
        stmt = (
            select(
                ChatChannelSlackCredential
            )
            .where(
                ChatChannelSlackCredential
                .channel_id
                == channel_id
            )
        )

        return (
            db.execute(
                stmt
            )
            .scalars()
            .first()
        )

    def get_by_team_id(
        self,
        db: Session,
        slack_team_id: str,
    ) -> (
        ChatChannelSlackCredential
        | None
    ):
        stmt = (
            select(
                ChatChannelSlackCredential
            )
            .where(
                ChatChannelSlackCredential
                .slack_team_id
                == slack_team_id
            )
        )

        return (
            db.execute(
                stmt
            )
            .scalars()
            .first()
        )

    def get_for_channel_and_team(
        self,
        db: Session,
        channel_id: UUID,
        slack_team_id: str,
    ) -> (
        ChatChannelSlackCredential
        | None
    ):
        stmt = (
            select(
                ChatChannelSlackCredential
            )
            .where(
                ChatChannelSlackCredential
                .channel_id
                == channel_id,

                ChatChannelSlackCredential
                .slack_team_id
                == slack_team_id,
            )
        )

        return (
            db.execute(
                stmt
            )
            .scalars()
            .first()
        )