from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    case,
    func,
    select,
)
from sqlalchemy.orm import Session

from app.models.conversation import (
    Conversation,
)
from app.models.conversation_message import (
    ConversationMessage,
)


class ChatChannelMetricsService:

    def get_metrics(
        self,
        db: Session,
        tenant_id: UUID,
        chat_channel_id: UUID,
    ) -> dict:
        conversation_count = (
            self._get_conversation_count(
                db=db,
                tenant_id=tenant_id,
                chat_channel_id=(
                    chat_channel_id
                ),
            )
        )

        (
            message_count,
            user_message_count,
            assistant_message_count,
            last_message_at,
        ) = self._get_message_metrics(
            db=db,
            tenant_id=tenant_id,
            chat_channel_id=(
                chat_channel_id
            ),
        )

        last_conversation_at = (
            self._get_last_conversation_activity(
                db=db,
                tenant_id=tenant_id,
                chat_channel_id=(
                    chat_channel_id
                ),
            )
        )

        last_activity_at = (
            self._latest_datetime(
                last_message_at,
                last_conversation_at,
            )
        )

        return {
            "conversation_count":
                conversation_count,

            "message_count":
                message_count,

            "user_message_count":
                user_message_count,

            "assistant_message_count":
                assistant_message_count,

            "last_activity_at":
                last_activity_at,
        }

    def _get_conversation_count(
        self,
        db: Session,
        tenant_id: UUID,
        chat_channel_id: UUID,
    ) -> int:
        stmt = (
            select(
                func.count(
                    Conversation.id
                )
            )
            .where(
                Conversation.tenant_id
                == tenant_id,

                Conversation.chat_channel_id
                == chat_channel_id,

                Conversation.user_id
                .is_(None),
            )
        )

        value = db.scalar(
            stmt
        )

        return int(
            value or 0
        )

    def _get_message_metrics(
        self,
        db: Session,
        tenant_id: UUID,
        chat_channel_id: UUID,
    ) -> tuple[
        int,
        int,
        int,
        datetime | None,
    ]:
        stmt = (
            select(
                func.count(
                    ConversationMessage.id
                ),

                func.sum(
                    case(
                        (
                            ConversationMessage.role
                            == "user",
                            1,
                        ),
                        else_=0,
                    )
                ),

                func.sum(
                    case(
                        (
                            ConversationMessage.role
                            == "assistant",
                            1,
                        ),
                        else_=0,
                    )
                ),

                func.max(
                    ConversationMessage.created_at
                ),
            )
            .join(
                Conversation,
                Conversation.id
                == ConversationMessage
                .conversation_id,
            )
            .where(
                Conversation.tenant_id
                == tenant_id,

                Conversation.chat_channel_id
                == chat_channel_id,

                Conversation.user_id
                .is_(None),
            )
        )

        row = db.execute(
            stmt
        ).one()

        return (
            int(
                row[0]
                or 0
            ),
            int(
                row[1]
                or 0
            ),
            int(
                row[2]
                or 0
            ),
            row[3],
        )

    def _get_last_conversation_activity(
        self,
        db: Session,
        tenant_id: UUID,
        chat_channel_id: UUID,
    ) -> datetime | None:
        stmt = (
            select(
                func.max(
                    Conversation.updated_at
                )
            )
            .where(
                Conversation.tenant_id
                == tenant_id,

                Conversation.chat_channel_id
                == chat_channel_id,

                Conversation.user_id
                .is_(None),
            )
        )

        return db.scalar(
            stmt
        )

    def _latest_datetime(
        self,
        first:
            datetime | None,
        second:
            datetime | None,
    ) -> datetime | None:
        values = [
            value
            for value
            in (
                first,
                second,
            )
            if value is not None
        ]

        if not values:
            return None

        return max(
            values
        )