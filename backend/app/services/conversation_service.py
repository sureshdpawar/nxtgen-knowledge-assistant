from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation import (
    Conversation,
)
from app.models.conversation_message import (
    ConversationMessage,
)
from app.repositories.conversation_message_repository import (
    ConversationMessageRepository,
)
from app.repositories.conversation_repository import (
    ConversationRepository,
)


class ConversationService:

    def __init__(self):
        self.conversation_repository = (
            ConversationRepository()
        )

        self.message_repository = (
            ConversationMessageRepository()
        )

    # ---------------------------------------------------------
    # Internal authenticated UI conversations
    # ---------------------------------------------------------

    def create_conversation(
        self,
        db: Session,
        tenant_id: UUID,
        user_id: UUID,
        knowledge_base_id: UUID,
        title: str,
    ) -> Conversation:
        conversation = Conversation(
            tenant_id=tenant_id,
            user_id=user_id,
            chat_channel_id=None,
            knowledge_base_id=(
                knowledge_base_id
            ),
            title=title,
        )

        db.add(
            conversation
        )

        db.commit()

        db.refresh(
            conversation
        )

        return conversation

    def get_conversation(
        self,
        db: Session,
        tenant_id: UUID,
        user_id: UUID,
        conversation_id: UUID,
    ) -> Conversation | None:
        stmt = (
            select(
                Conversation
            )
            .where(
                Conversation.id
                == conversation_id,

                Conversation.tenant_id
                == tenant_id,

                Conversation.user_id
                == user_id,

                Conversation.chat_channel_id
                .is_(None),
            )
        )

        return db.scalar(
            stmt
        )

    def get_or_create_conversation(
        self,
        db: Session,
        tenant_id: UUID,
        user_id: UUID,
        knowledge_base_id: UUID,
        conversation_id:
            UUID | None,
        title: str,
    ) -> Conversation:
        if conversation_id:
            conversation = (
                self.get_conversation(
                    db=db,
                    tenant_id=tenant_id,
                    user_id=user_id,
                    conversation_id=(
                        conversation_id
                    ),
                )
            )

            if conversation:
                if (
                    conversation
                    .knowledge_base_id
                    != knowledge_base_id
                ):
                    raise ValueError(
                        "Conversation belongs "
                        "to a different "
                        "knowledge base."
                    )

                return conversation

        return (
            self.create_conversation(
                db=db,
                tenant_id=tenant_id,
                user_id=user_id,
                knowledge_base_id=(
                    knowledge_base_id
                ),
                title=title,
            )
        )

    # ---------------------------------------------------------
    # External channel conversations
    # ---------------------------------------------------------

    def create_channel_conversation(
        self,
        db: Session,
        tenant_id: UUID,
        chat_channel_id: UUID,
        knowledge_base_id: UUID,
        title: str,
    ) -> Conversation:
        conversation = Conversation(
            tenant_id=tenant_id,
            user_id=None,
            chat_channel_id=(
                chat_channel_id
            ),
            knowledge_base_id=(
                knowledge_base_id
            ),
            title=title,
        )

        db.add(
            conversation
        )

        db.commit()

        db.refresh(
            conversation
        )

        return conversation

    def get_channel_conversation(
        self,
        db: Session,
        tenant_id: UUID,
        chat_channel_id: UUID,
        conversation_id: UUID,
    ) -> Conversation | None:
        stmt = (
            select(
                Conversation
            )
            .where(
                Conversation.id
                == conversation_id,

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

    def get_or_create_channel_conversation(
        self,
        db: Session,
        tenant_id: UUID,
        chat_channel_id: UUID,
        knowledge_base_id: UUID,
        conversation_id:
            UUID | None,
        title: str,
    ) -> Conversation:
        if conversation_id:
            conversation = (
                self.get_channel_conversation(
                    db=db,
                    tenant_id=tenant_id,
                    chat_channel_id=(
                        chat_channel_id
                    ),
                    conversation_id=(
                        conversation_id
                    ),
                )
            )

            if conversation is None:
                raise ValueError(
                    "Channel session was not found."
                )

            if (
                conversation
                .knowledge_base_id
                != knowledge_base_id
            ):
                raise ValueError(
                    "Channel session belongs "
                    "to a different "
                    "knowledge base."
                )

            return conversation

        return (
            self.create_channel_conversation(
                db=db,
                tenant_id=tenant_id,
                chat_channel_id=(
                    chat_channel_id
                ),
                knowledge_base_id=(
                    knowledge_base_id
                ),
                title=title,
            )
        )

    def list_channel_conversations(
        self,
        db: Session,
        tenant_id: UUID,
        chat_channel_id: UUID,
    ) -> list[
        Conversation
    ]:
        stmt = (
            select(
                Conversation
            )
            .where(
                Conversation.tenant_id
                == tenant_id,

                Conversation.chat_channel_id
                == chat_channel_id,

                Conversation.user_id
                .is_(None),
            )
            .order_by(
                Conversation
                .updated_at
                .desc()
            )
        )

        return list(
            db.scalars(
                stmt
            ).all()
        )

    def get_channel_conversation_with_messages(
        self,
        db: Session,
        tenant_id: UUID,
        chat_channel_id: UUID,
        conversation_id: UUID,
    ) -> Conversation | None:
        conversation = (
            self.get_channel_conversation(
                db=db,
                tenant_id=tenant_id,
                chat_channel_id=(
                    chat_channel_id
                ),
                conversation_id=(
                    conversation_id
                ),
            )
        )

        if conversation is None:
            return None

        #
        # Trigger relationship load before
        # returning the SQLAlchemy model.
        #
        conversation.messages

        return conversation

    def delete_channel_conversation(
        self,
        db: Session,
        tenant_id: UUID,
        chat_channel_id: UUID,
        conversation_id: UUID,
    ) -> bool:
        conversation = (
            self.get_channel_conversation(
                db=db,
                tenant_id=tenant_id,
                chat_channel_id=(
                    chat_channel_id
                ),
                conversation_id=(
                    conversation_id
                ),
            )
        )

        if conversation is None:
            return False

        db.delete(
            conversation
        )

        db.commit()

        return True

    # ---------------------------------------------------------
    # Messages
    # ---------------------------------------------------------

    def add_message(
        self,
        db: Session,
        conversation_id: UUID,
        role: str,
        content: str,
        citations:
            list | None = None,
        token_usage:
            dict | None = None,
    ) -> ConversationMessage:
        message = (
            ConversationMessage(
                conversation_id=(
                    conversation_id
                ),
                role=role,
                content=content,
                citations=(
                    citations
                    or []
                ),
                token_usage=(
                    token_usage
                    or {}
                ),
            )
        )

        db.add(
            message
        )

        db.commit()

        db.refresh(
            message
        )

        return message

    def save_user_message(
        self,
        db: Session,
        conversation_id: UUID,
        content: str,
    ) -> ConversationMessage:
        return self.add_message(
            db=db,
            conversation_id=(
                conversation_id
            ),
            role="user",
            content=content,
        )

    def save_assistant_message(
        self,
        db: Session,
        conversation_id: UUID,
        content: str,
        citations: list,
        token_usage: dict,
    ) -> ConversationMessage:
        return self.add_message(
            db=db,
            conversation_id=(
                conversation_id
            ),
            role="assistant",
            content=content,
            citations=citations,
            token_usage=(
                token_usage
            ),
        )

    def get_messages(
        self,
        db: Session,
        conversation_id: UUID,
    ) -> list[
        ConversationMessage
    ]:
        stmt = (
            select(
                ConversationMessage
            )
            .where(
                ConversationMessage
                .conversation_id
                == conversation_id
            )
            .order_by(
                ConversationMessage
                .created_at
            )
        )

        return list(
            db.scalars(
                stmt
            ).all()
        )

    # ---------------------------------------------------------
    # Internal UI conversation management
    # ---------------------------------------------------------

    def list_conversations(
        self,
        db: Session,
        tenant_id: UUID,
        user_id: UUID,
    ) -> list[
        Conversation
    ]:
        stmt = (
            select(
                Conversation
            )
            .where(
                Conversation.tenant_id
                == tenant_id,

                Conversation.user_id
                == user_id,

                Conversation.chat_channel_id
                .is_(None),
            )
            .order_by(
                Conversation
                .updated_at
                .desc()
            )
        )

        return list(
            db.scalars(
                stmt
            ).all()
        )

    def get_conversation_with_messages(
        self,
        db: Session,
        tenant_id: UUID,
        user_id: UUID,
        conversation_id: UUID,
    ) -> Conversation | None:
        conversation = (
            self.get_conversation(
                db=db,
                tenant_id=tenant_id,
                user_id=user_id,
                conversation_id=(
                    conversation_id
                ),
            )
        )

        if conversation is None:
            return None

        conversation.messages

        return conversation

    def delete_conversation(
        self,
        db: Session,
        tenant_id: UUID,
        user_id: UUID,
        conversation_id: UUID,
    ) -> bool:
        conversation = (
            self.get_conversation(
                db=db,
                tenant_id=tenant_id,
                user_id=user_id,
                conversation_id=(
                    conversation_id
                ),
            )
        )

        if conversation is None:
            return False

        db.delete(
            conversation
        )

        db.commit()

        return True