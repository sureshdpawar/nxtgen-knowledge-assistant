from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    JSON,
    String,
    Text,
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
    from app.models.agent_run import AgentRun
    from app.models.tenant import Tenant


class AgentOnlineEvalResult(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    """
    Online quality evaluation of an already-executed AgentRun.

    This record never causes agent replay and never executes tools.
    It evaluates persisted production/staging behavior only.
    """

    __tablename__ = "agent_online_eval_result"
    __table_args__ = (
        UniqueConstraint(
            "agent_run_id",
            name="uq_agent_online_eval_result_agent_run_id",
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

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="pending",
        server_default="pending",
        index=True,
    )

    sample_reason: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="manual",
        server_default="manual",
        index=True,
    )

    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    actual_answer: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    tools_used: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    task_quality_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    execution_health_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    overall_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    passed: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        index=True,
    )

    evaluated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    metrics: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    evaluation_metadata: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    tenant: Mapped["Tenant"] = relationship(
        "Tenant",
    )

    agent: Mapped["Agent"] = relationship(
        "Agent",
    )

    agent_run: Mapped["AgentRun"] = relationship(
        "AgentRun",
    )
