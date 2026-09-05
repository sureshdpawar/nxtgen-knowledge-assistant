from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import AgentActionApprovalStatus
from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin


if TYPE_CHECKING:
    from app.models.agent import Agent
    from app.models.agent_run import AgentRun
    from app.models.user import User


class AgentActionApproval(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    """
    Product-level approval record for one paused agent checkpoint.

    A single LangGraph interrupt may contain multiple tool calls.
    Therefore `actions` mirrors the interrupt bundle and the approval
    decision applies to that bundle as one resumable execution unit.
    """

    __tablename__ = "agent_action_approval"

    __table_args__ = (
        UniqueConstraint(
            "agent_run_id",
            "checkpoint_id",
            name=(
                "uq_agent_action_approval_"
                "run_checkpoint"
            ),
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

    agent_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "agent.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    agent_run_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "agent_run.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    checkpoint_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    actions: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    status: Mapped[
        AgentActionApprovalStatus
    ] = mapped_column(
        Enum(
            AgentActionApprovalStatus,
        ),
        default=(
            AgentActionApprovalStatus
            .PENDING
        ),
        server_default=(
            AgentActionApprovalStatus
            .PENDING
            .value
        ),
        nullable=False,
        index=True,
    )

    requested_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True,
        ),
        default=lambda: datetime.now(
            timezone.utc,
        ),
        nullable=False,
        index=True,
    )

    decided_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(
            timezone=True,
        ),
        nullable=True,
    )

    decided_by_user_id: Mapped[
        UUID | None
    ] = mapped_column(
        ForeignKey(
            "app_user.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    decision_reason: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    agent: Mapped["Agent"] = relationship(
        "Agent",
    )

    run: Mapped["AgentRun"] = relationship(
        "AgentRun",
    )

    decided_by: Mapped[
        "User | None"
    ] = relationship(
        "User",
        foreign_keys=[
            decided_by_user_id
        ],
    )
