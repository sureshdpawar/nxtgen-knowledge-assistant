import logging
import re

from sqlalchemy.orm import Session

from app.core.enums import (
    ChatChannelStatus,
    ChatChannelType,
)
from app.models.chat_channel import (
    ChatChannel,
)
from app.services.channel_chat_service import (
    ChannelChatService,
)
from app.services.chat_channel_slack_service import (
    ChatChannelSlackService,
)
from app.services.slack_api_service import (
    SlackApiService,
)
from app.services.slack_conversation_service import (
    SlackConversationService,
)


logger = logging.getLogger(
    "nxtgen.slack"
)


class SlackEventService:

    def __init__(self):
        self.slack_service = (
            ChatChannelSlackService()
        )

        self.chat_service = (
            ChannelChatService()
        )

        self.api_service = (
            SlackApiService()
        )

        self.conversation_service = (
            SlackConversationService()
        )

    # -----------------------------------------------------
    # Public event handlers
    # -----------------------------------------------------

    def process_app_mention(
        self,
        db: Session,
        slack_team_id: str,
        event: dict,
    ) -> None:
        self._process_message(
            db=db,
            slack_team_id=(
                slack_team_id
            ),
            event=(
                event
            ),
            is_direct_message=False,
        )

    def process_direct_message(
        self,
        db: Session,
        slack_team_id: str,
        event: dict,
    ) -> None:
        self._process_message(
            db=db,
            slack_team_id=(
                slack_team_id
            ),
            event=(
                event
            ),
            is_direct_message=True,
        )

    # -----------------------------------------------------
    # Shared Slack message processing
    # -----------------------------------------------------

    def _process_message(
        self,
        db: Session,
        slack_team_id: str,
        event: dict,
        is_direct_message: bool,
    ) -> None:
        credential = (
            self.slack_service
            .get_credential_by_team_id(
                db=db,
                slack_team_id=(
                    slack_team_id
                ),
            )
        )

        if credential is None:
            logger.warning(
                "Slack credential not found "
                "team_id=%s",
                slack_team_id,
            )

            return

        channel = db.get(
            ChatChannel,
            credential.channel_id,
        )

        if channel is None:
            logger.warning(
                "Slack NXTGEN channel "
                "not found "
                "team_id=%s",
                slack_team_id,
            )

            return

        if (
            channel.type
            != ChatChannelType.SLACK
        ):
            logger.warning(
                "Slack credential belongs "
                "to non-Slack channel "
                "channel_id=%s",
                channel.id,
            )

            return

        if (
            channel.status
            != ChatChannelStatus.ACTIVE
        ):
            logger.info(
                "Ignoring Slack message "
                "for inactive channel "
                "channel_id=%s",
                channel.id,
            )

            return

        configuration = (
            channel.configuration
            or {}
        )

        # -------------------------------------------------
        # Check configured message behavior
        # -------------------------------------------------

        if is_direct_message:
            if not bool(
                configuration.get(
                    "respond_to_direct_messages",
                    False,
                )
            ):
                logger.info(
                    "Slack DMs disabled "
                    "channel_id=%s",
                    channel.id,
                )

                return

        else:
            if not bool(
                configuration.get(
                    "respond_to_mentions",
                    True,
                )
            ):
                logger.info(
                    "Slack mentions disabled "
                    "channel_id=%s",
                    channel.id,
                )

                return

        # -------------------------------------------------
        # Ignore bot-generated events
        # -------------------------------------------------

        if (
            event.get(
                "bot_id"
            )
            is not None
        ):
            return

        if (
            event.get(
                "subtype"
            )
            == "bot_message"
        ):
            return

        # -------------------------------------------------
        # Resolve Slack channel
        # -------------------------------------------------

        slack_channel_id = (
            event.get(
                "channel"
            )
        )

        if not slack_channel_id:
            logger.warning(
                "Slack message missing "
                "channel ID "
                "team_id=%s",
                slack_team_id,
            )

            return

        # -------------------------------------------------
        # Apply allowed-channel restriction
        # only to normal Slack channels.
        #
        # DMs should not be checked against
        # allowed_slack_channel_ids.
        # -------------------------------------------------

        if (
            not is_direct_message
            and not self._channel_is_allowed(
                configuration=(
                    configuration
                ),
                slack_channel_id=(
                    slack_channel_id
                ),
            )
        ):
            logger.info(
                "Ignoring Slack message "
                "from disallowed channel "
                "channel_id=%s "
                "slack_channel_id=%s",
                channel.id,
                slack_channel_id,
            )

            return

        # -------------------------------------------------
        # Extract query
        # -------------------------------------------------

        raw_text = (
            event.get(
                "text"
            )
            or ""
        )

        if is_direct_message:
            query = (
                raw_text.strip()
            )

        else:
            query = (
                self._clean_mention(
                    text=(
                        raw_text
                    ),
                    bot_user_id=(
                        credential
                        .bot_user_id
                    ),
                )
            )

        if not query:
            if not is_direct_message:
                self.api_service.post_message(
                    bot_token=(
                        credential
                        .bot_token
                    ),
                    channel_id=(
                        slack_channel_id
                    ),
                    text=(
                        "Please include a "
                        "question when you "
                        "mention me."
                    ),
                    thread_ts=(
                        self._get_reply_thread_ts(
                            event
                        )
                    ),
                )

            return

        slack_user_id = (
            event.get(
                "user"
            )
        )

        # -------------------------------------------------
        # Resolve Slack conversation key
        # -------------------------------------------------

        slack_thread_ts = (
            self._resolve_conversation_thread(
                event=(
                    event
                ),
                is_direct_message=(
                    is_direct_message
                ),
            )
        )

        if not slack_thread_ts:
            logger.warning(
                "Unable to determine Slack "
                "conversation key "
                "channel_id=%s",
                channel.id,
            )

            return

        # -------------------------------------------------
        # Resolve existing NXTGEN conversation
        # -------------------------------------------------

        conversation_id = (
            self.conversation_service
            .get_conversation_id(
                db=db,
                channel_id=(
                    channel.id
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
            )
        )

        logger.info(
            "Processing Slack message "
            "channel_id=%s "
            "team_id=%s "
            "slack_channel_id=%s "
            "direct_message=%s "
            "existing_conversation_id=%s",
            channel.id,
            slack_team_id,
            slack_channel_id,
            is_direct_message,
            conversation_id,
        )

        # -------------------------------------------------
        # Run existing NXTGEN channel chat pipeline
        # -------------------------------------------------

        result = (
            self.chat_service.chat(
                db=db,
                tenant_id=(
                    channel.tenant_id
                ),
                chat_channel_id=(
                    channel.id
                ),
                knowledge_base_id=(
                    channel
                    .knowledge_base_id
                ),
                session_id=(
                    conversation_id
                ),
                query=(
                    query
                ),
            )
        )

        returned_conversation_id = (
            result.get(
                "session_id"
            )
        )

        # -------------------------------------------------
        # Create Slack → NXTGEN conversation mapping
        #
        # This is the syntax correction you needed:
        # the chained call is wrapped in parentheses.
        # -------------------------------------------------

        if (
            conversation_id is None
            and returned_conversation_id
        ):
            (
                self.conversation_service
                .create_mapping(
                    db=db,
                    channel_id=(
                        channel.id
                    ),
                    conversation_id=(
                        returned_conversation_id
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

            logger.info(
                "Slack conversation mapping "
                "created "
                "channel_id=%s "
                "conversation_id=%s "
                "slack_thread_ts=%s",
                channel.id,
                returned_conversation_id,
                slack_thread_ts,
            )

        # -------------------------------------------------
        # Build answer
        # -------------------------------------------------

        answer = (
            result.get(
                "answer"
            )
            or (
                "I couldn't generate "
                "an answer."
            )
        )

        sources = (
            result.get(
                "sources"
            )
            or []
        )

        response_text = (
            self._build_response_text(
                answer=(
                    answer
                ),
                sources=(
                    sources
                ),
            )
        )

        # -------------------------------------------------
        # Slack reply behavior
        #
        # app_mention:
        # reply inside Slack thread
        #
        # DM:
        # send directly into DM channel
        # -------------------------------------------------

        reply_thread_ts = None

        if not is_direct_message:
            reply_thread_ts = (
                self._get_reply_thread_ts(
                    event
                )
            )

        self.api_service.post_message(
            bot_token=(
                credential
                .bot_token
            ),
            channel_id=(
                slack_channel_id
            ),
            text=(
                response_text
            ),
            thread_ts=(
                reply_thread_ts
            ),
        )

        logger.info(
            "Slack response sent "
            "channel_id=%s "
            "slack_channel_id=%s "
            "conversation_id=%s "
            "direct_message=%s",
            channel.id,
            slack_channel_id,
            (
                conversation_id
                or returned_conversation_id
            ),
            is_direct_message,
        )

    # -----------------------------------------------------
    # Conversation key
    # -----------------------------------------------------

    def _resolve_conversation_thread(
        self,
        event: dict,
        is_direct_message: bool,
    ) -> str | None:
        if is_direct_message:
            #
            # For DMs, use the Slack DM
            # channel ID as the conversation
            # key.
            #
            # This gives each user/bot DM
            # channel one continuous NXTGEN
            # conversation.
            #
            slack_channel_id = (
                event.get(
                    "channel"
                )
            )

            if slack_channel_id:
                return str(
                    slack_channel_id
                )

            return None

        #
        # Existing Slack thread.
        #
        thread_ts = (
            event.get(
                "thread_ts"
            )
        )

        if thread_ts:
            return str(
                thread_ts
            )

        #
        # First message in a new Slack
        # thread. The mention message itself
        # becomes the thread root.
        #
        event_ts = (
            event.get(
                "ts"
            )
        )

        if event_ts:
            return str(
                event_ts
            )

        return None

    # -----------------------------------------------------
    # Reply thread
    # -----------------------------------------------------

    def _get_reply_thread_ts(
        self,
        event: dict,
    ) -> str | None:
        thread_ts = (
            event.get(
                "thread_ts"
            )
        )

        if thread_ts:
            return str(
                thread_ts
            )

        event_ts = (
            event.get(
                "ts"
            )
        )

        if event_ts:
            return str(
                event_ts
            )

        return None

    # -----------------------------------------------------
    # Allowed Slack channels
    # -----------------------------------------------------

    def _channel_is_allowed(
        self,
        configuration: dict,
        slack_channel_id: str,
    ) -> bool:
        allowed_channels = (
            configuration.get(
                "allowed_slack_channel_ids"
            )
            or []
        )

        #
        # Empty allowed list means all
        # Slack channels where the app
        # is available.
        #
        if not allowed_channels:
            return True

        return (
            slack_channel_id
            in allowed_channels
        )

    # -----------------------------------------------------
    # Strip Slack bot mention
    # -----------------------------------------------------

    def _clean_mention(
        self,
        text: str,
        bot_user_id:
            str | None,
    ) -> str:
        cleaned = (
            text.strip()
        )

        if bot_user_id:
            cleaned = re.sub(
                (
                    rf"<@"
                    rf"{re.escape(bot_user_id)}"
                    rf">"
                ),
                "",
                cleaned,
            )

        else:
            #
            # MVP fallback if bot_user_id
            # was not configured.
            #
            cleaned = re.sub(
                r"<@[A-Z0-9]+>",
                "",
                cleaned,
                count=1,
            )

        return (
            cleaned.strip()
        )

    # -----------------------------------------------------
    # Format Slack answer + citations
    # -----------------------------------------------------

    def _build_response_text(
        self,
        answer: str,
        sources: list,
    ) -> str:
        text = (
            answer.strip()
        )

        if not sources:
            return text

        document_names = []

        seen = set()

        for source in sources:
            if not isinstance(
                source,
                dict,
            ):
                continue

            document_name = (
                source.get(
                    "document_name"
                )
            )

            if not document_name:
                continue

            document_name = str(
                document_name
            )

            if (
                document_name
                in seen
            ):
                continue

            seen.add(
                document_name
            )

            document_names.append(
                document_name
            )

        if not document_names:
            return text

        source_lines = [
            f"• {name}"
            for name
            in document_names[:5]
        ]

        return (
            f"{text}\n\n"
            "*Sources*\n"
            + "\n".join(
                source_lines
            )
        )