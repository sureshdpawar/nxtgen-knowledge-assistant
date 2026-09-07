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
from app.models.agent import Agent
from app.models.user import User


class UserAgentAccess(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "user_agent_access"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "agent_id",
            name="uq_user_agent_access",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "app_user.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    agent_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "agent.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    user: Mapped["User"] = relationship(
        "User",
    )

    agent: Mapped["Agent"] = relationship(
        "Agent",
    )
