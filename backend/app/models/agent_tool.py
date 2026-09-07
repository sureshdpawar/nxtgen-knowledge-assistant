from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Enum,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.core.enums import (
    ToolExecutionPolicy,
)
from app.db.base import Base
from app.db.mixins import (
    TimestampMixin,
    UUIDMixin,
)


if TYPE_CHECKING:
    from app.models.agent import Agent
    from app.models.tool_definition import (
        ToolDefinition,
    )


class AgentTool(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "agent_tool"

    __table_args__ = (
        UniqueConstraint(
            "agent_id",
            "tool_id",
            name="uq_agent_tool",
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

    tool_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "tool_definition.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    execution_policy: Mapped[
        ToolExecutionPolicy
    ] = mapped_column(
        Enum(
            ToolExecutionPolicy,
        ),
        default=(
            ToolExecutionPolicy
            .HUMAN_APPROVAL
        ),
        server_default=(
            ToolExecutionPolicy
            .HUMAN_APPROVAL.value
        ),
        nullable=False,
    )

    agent: Mapped[
        "Agent"
    ] = relationship(
        "Agent",
        back_populates="tool_links",
    )

    tool: Mapped[
        "ToolDefinition"
    ] = relationship(
        "ToolDefinition",
        back_populates="agent_links",
    )
