from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    ForeignKey,
    UniqueConstraint,
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


if TYPE_CHECKING:
    from app.models.agent import Agent
    from app.models.knowledge_base import KnowledgeBase


class AgentKnowledgeBase(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = (
        "agent_knowledge_base"
    )

    __table_args__ = (
        UniqueConstraint(
            "agent_id",
            "knowledge_base_id",
            name=(
                "uq_agent_knowledge_base"
            ),
        ),
    )

    agent_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "agent.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    knowledge_base_id: Mapped[
        UUID
    ] = mapped_column(
        ForeignKey(
            "knowledge_base.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    agent: Mapped[
        "Agent"
    ] = relationship(
        "Agent",
        back_populates=
            "knowledge_base_links",
    )

    knowledge_base: Mapped[
        "KnowledgeBase"
    ] = relationship(
        "KnowledgeBase",
    )