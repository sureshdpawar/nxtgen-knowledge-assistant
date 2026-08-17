from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
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
    ToolRiskLevel,
    ToolType,
)
from app.db.base import Base
from app.db.mixins import (
    TimestampMixin,
    UUIDMixin,
)


if TYPE_CHECKING:
    from app.models.agent_tool import (
        AgentTool,
    )
    from app.models.integration import (
        Integration,
    )


class ToolDefinition(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "tool_definition"

    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "tenant.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    integration_id: Mapped[
        UUID | None
    ] = mapped_column(
        ForeignKey(
            "integration.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    tool_type: Mapped[
        ToolType
    ] = mapped_column(
        Enum(
            ToolType,
        ),
        nullable=False,
        index=True,
    )

    risk_level: Mapped[
        ToolRiskLevel
    ] = mapped_column(
        Enum(
            ToolRiskLevel,
        ),
        default=
            ToolRiskLevel.READ,
        server_default=
            ToolRiskLevel.READ.value,
        nullable=False,
    )

    input_schema: Mapped[
        dict
    ] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    configuration: Mapped[
        dict | None
    ] = mapped_column(
        JSON,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
    )

    integration: Mapped[
        "Integration | None"
    ] = relationship(
        "Integration",
        back_populates="tools",
    )

    agent_links: Mapped[
        list["AgentTool"]
    ] = relationship(
        "AgentTool",
        back_populates="tool",
        cascade="all, delete-orphan",
    )