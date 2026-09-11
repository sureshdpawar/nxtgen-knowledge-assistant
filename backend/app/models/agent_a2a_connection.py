from __future__ import annotations

from uuid import UUID

from sqlalchemy import (
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base import Base
from app.db.mixins import (
    TimestampMixin,
    UUIDMixin,
)


class AgentA2AConnection(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "agent_a2a_connection"
    __table_args__ = (
        UniqueConstraint(
            "source_agent_id",
            "target_agent_id",
            name="uq_agent_a2a_connection_source_target",
        ),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "tenant.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    source_agent_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "agent.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    target_agent_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "agent.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    created_by: Mapped[UUID] = mapped_column(
        ForeignKey(
            "app_user.id",
        ),
        nullable=False,
    )
