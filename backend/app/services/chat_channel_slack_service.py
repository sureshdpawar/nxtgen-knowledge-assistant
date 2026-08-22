from uuid import UUID

from sqlalchemy.orm import Session

from app.core.enums import (
    ChatChannelType,
)
from app.models.chat_channel_slack_credential import (
    ChatChannelSlackCredential,
)
from app.models.user import (
    User,
)
from app.repositories.chat_channel_slack_credential_repository import (
    ChatChannelSlackCredentialRepository,
)
from app.schemas.chat_channel_slack import (
    ChatChannelSlackConnectRequest,
    ChatChannelSlackResponse,
)
from app.services.chat_channel_service import (
    ChatChannelService,
)


class ChatChannelSlackService:

    def __init__(self):
        self.channel_service = (
            ChatChannelService()
        )

        self.repository = (
            ChatChannelSlackCredentialRepository()
        )

    def get_configuration(
        self,
        db: Session,
        current_user: User,
        channel_id: UUID,
    ) -> ChatChannelSlackResponse:
        channel = (
            self.channel_service
            .get_channel(
                db=db,
                current_user=(
                    current_user
                ),
                channel_id=(
                    channel_id
                ),
            )
        )

        self._require_slack_channel(
            channel.type
        )

        credential = (
            self.repository
            .get_by_channel(
                db=db,
                channel_id=(
                    channel.id
                ),
            )
        )

        if credential is None:
            raise ValueError(
                "Slack workspace is not "
                "configured for this channel."
            )

        configuration = (
            channel.configuration
            or {}
        )

        return (
            ChatChannelSlackResponse(
                slack_team_id=(
                    credential
                    .slack_team_id
                ),
                slack_team_name=(
                    credential
                    .slack_team_name
                ),
                bot_user_id=(
                    credential
                    .bot_user_id
                ),
                configured=True,
                respond_to_mentions=(
                    bool(
                        configuration.get(
                            "respond_to_mentions",
                            True,
                        )
                    )
                ),
                respond_to_direct_messages=(
                    bool(
                        configuration.get(
                            "respond_to_direct_messages",
                            False,
                        )
                    )
                ),
                allowed_slack_channel_ids=(
                    list(
                        configuration.get(
                            "allowed_slack_channel_ids",
                            [],
                        )
                        or []
                    )
                ),
            )
        )

    def connect(
        self,
        db: Session,
        current_user: User,
        channel_id: UUID,
        payload:
            ChatChannelSlackConnectRequest,
    ) -> ChatChannelSlackResponse:
        channel = (
            self.channel_service
            .get_channel(
                db=db,
                current_user=(
                    current_user
                ),
                channel_id=(
                    channel_id
                ),
            )
        )

        self._require_slack_channel(
            channel.type
        )

        slack_team_id = (
            payload
            .slack_team_id
            .strip()
        )

        bot_token = (
            payload
            .bot_token
            .strip()
        )

        signing_secret = (
            payload
            .signing_secret
            .strip()
        )

        if not slack_team_id:
            raise ValueError(
                "Slack team ID is required."
            )

        if not bot_token:
            raise ValueError(
                "Slack bot token is required."
            )

        if not signing_secret:
            raise ValueError(
                "Slack signing secret is required."
            )

        existing_for_team = (
            self.repository
            .get_by_team_id(
                db=db,
                slack_team_id=(
                    slack_team_id
                ),
            )
        )

        if (
            existing_for_team
            is not None
            and existing_for_team
            .channel_id
            != channel.id
        ):
            raise ValueError(
                "This Slack workspace is "
                "already connected to another "
                "channel."
            )

        credential = (
            self.repository
            .get_by_channel(
                db=db,
                channel_id=(
                    channel.id
                ),
            )
        )

        if credential is None:
            credential = (
                ChatChannelSlackCredential(
                    channel_id=(
                        channel.id
                    ),
                    slack_team_id=(
                        slack_team_id
                    ),
                    slack_team_name=(
                        self._clean_optional(
                            payload
                            .slack_team_name
                        )
                    ),
                    bot_user_id=(
                        self._clean_optional(
                            payload
                            .bot_user_id
                        )
                    ),
                    bot_token=(
                        bot_token
                    ),
                    signing_secret=(
                        signing_secret
                    ),
                )
            )

            self.repository.create(
                db,
                credential,
            )

        else:
            credential.slack_team_id = (
                slack_team_id
            )

            credential.slack_team_name = (
                self._clean_optional(
                    payload
                    .slack_team_name
                )
            )

            credential.bot_user_id = (
                self._clean_optional(
                    payload
                    .bot_user_id
                )
            )

            credential.bot_token = (
                bot_token
            )

            credential.signing_secret = (
                signing_secret
            )

            self.repository.update(
                db,
                credential,
            )

        channel.configuration = {
            **(
                channel.configuration
                or {}
            ),
            "respond_to_mentions": (
                payload
                .respond_to_mentions
            ),
            "respond_to_direct_messages": (
                payload
                .respond_to_direct_messages
            ),
            "allowed_slack_channel_ids": (
                self._normalize_channel_ids(
                    payload
                    .allowed_slack_channel_ids
                )
            ),
        }

        db.commit()

        db.refresh(
            credential
        )

        db.refresh(
            channel
        )

        return (
            self.get_configuration(
                db=db,
                current_user=(
                    current_user
                ),
                channel_id=(
                    channel.id
                ),
            )
        )

    def disconnect(
        self,
        db: Session,
        current_user: User,
        channel_id: UUID,
    ) -> None:
        channel = (
            self.channel_service
            .get_channel(
                db=db,
                current_user=(
                    current_user
                ),
                channel_id=(
                    channel_id
                ),
            )
        )

        self._require_slack_channel(
            channel.type
        )

        credential = (
            self.repository
            .get_by_channel(
                db=db,
                channel_id=(
                    channel.id
                ),
            )
        )

        if credential is None:
            raise ValueError(
                "Slack workspace is not "
                "configured for this channel."
            )

        db.delete(
            credential
        )

        configuration = dict(
            channel.configuration
            or {}
        )

        configuration.pop(
            "respond_to_mentions",
            None,
        )

        configuration.pop(
            "respond_to_direct_messages",
            None,
        )

        configuration.pop(
            "allowed_slack_channel_ids",
            None,
        )

        channel.configuration = (
            configuration
        )

        db.commit()

    def get_credential_by_team_id(
        self,
        db: Session,
        slack_team_id: str,
    ) -> (
        ChatChannelSlackCredential
        | None
    ):
        return (
            self.repository
            .get_by_team_id(
                db=db,
                slack_team_id=(
                    slack_team_id
                ),
            )
        )

    def _require_slack_channel(
        self,
        channel_type:
            ChatChannelType,
    ) -> None:
        if (
            channel_type
            != ChatChannelType.SLACK
        ):
            raise ValueError(
                "Slack configuration can "
                "only be used with SLACK "
                "channels."
            )

    def _clean_optional(
        self,
        value:
            str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return (
            value
            or None
        )

    def _normalize_channel_ids(
        self,
        channel_ids:
            list[str],
    ) -> list[str]:
        normalized = []

        seen = set()

        for channel_id in channel_ids:
            value = (
                channel_id
                .strip()
            )

            if not value:
                continue

            if value in seen:
                continue

            seen.add(
                value
            )

            normalized.append(
                value
            )

        return normalized