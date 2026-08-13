from uuid import UUID

from sqlalchemy import (
    ForeignKey,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base
from app.db.mixins import (
    TimestampMixin,
    UUIDMixin,
)


class Conversation(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "conversation"

    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenant.id"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("app_user.id"),
        nullable=False,
        index=True,
    )

    knowledge_base_id: Mapped[UUID] = mapped_column(
        ForeignKey("knowledge_base.id"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    tenant: Mapped["Tenant"] = relationship(
        "Tenant",
        back_populates="conversations",
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="conversations",
    )

    knowledge_base: Mapped["KnowledgeBase"] = relationship(
        "KnowledgeBase",
    )

    messages: Mapped[
        list["ConversationMessage"]
    ] = relationship(
        "ConversationMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by=
            "ConversationMessage.created_at",
    )