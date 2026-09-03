from datetime import (
    datetime,
    timezone,
)
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.core.enums import (
    AgentRunStatus,
)
from app.db.base import Base
from app.db.mixins import (
    TimestampMixin,
    UUIDMixin,
)


if TYPE_CHECKING:
    from app.models.agent import Agent
    from app.models.agent_run_step import (
        AgentRunStep,
    )
    from app.models.user import User


class AgentRun(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "agent_run"

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

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "app_user.id",
        ),
        nullable=False,
        index=True,
    )

    # Public conversation/thread identifier. LangGraph receives
    # an internally scoped thread key built from tenant+agent+
    # user+thread so checkpoint state cannot cross those scopes.
    thread_id: Mapped[
        UUID | None
    ] = mapped_column(
        nullable=True,
        index=True,
    )

    # Latest LangGraph checkpoint associated with this run.
    checkpoint_id: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True,
    )

    query: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    answer: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[
        AgentRunStatus
    ] = mapped_column(
        Enum(
            AgentRunStatus,
        ),
        default=
            AgentRunStatus.RUNNING,
        server_default=
            AgentRunStatus.RUNNING.value,
        nullable=False,
        index=True,
    )

    llm_calls: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )

    tools_used: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    duration_ms: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    error_message: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    started_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(
            timezone=True,
        ),
        default=lambda:
            datetime.now(
                timezone.utc,
            ),
        nullable=False,
    )

    completed_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(
            timezone=True,
        ),
        nullable=True,
    )

    agent: Mapped[
        "Agent"
    ] = relationship(
        "Agent",
    )

    user: Mapped[
        "User"
    ] = relationship(
        "User",
    )

    steps: Mapped[
        list[
            "AgentRunStep"
        ]
    ] = relationship(
        "AgentRunStep",
        back_populates="run",
        cascade=(
            "all, "
            "delete-orphan"
        ),
        order_by=(
            "AgentRunStep."
            "step_number"
        ),
    )
