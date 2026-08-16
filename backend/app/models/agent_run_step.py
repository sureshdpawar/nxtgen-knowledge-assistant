from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.core.enums import (
    AgentRunStepStatus,
    AgentRunStepType,
)
from app.db.base import Base
from app.db.mixins import (
    TimestampMixin,
    UUIDMixin,
)


if TYPE_CHECKING:
    from app.models.agent_run import (
        AgentRun,
    )


class AgentRunStep(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = (
        "agent_run_step"
    )

    run_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "agent_run.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    step_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    step_type: Mapped[
        AgentRunStepType
    ] = mapped_column(
        Enum(
            AgentRunStepType,
        ),
        nullable=False,
    )

    status: Mapped[
        AgentRunStepStatus
    ] = mapped_column(
        Enum(
            AgentRunStepStatus,
        ),
        default=
            AgentRunStepStatus.COMPLETED,
        server_default=
            AgentRunStepStatus
            .COMPLETED
            .value,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    input_data: Mapped[
        dict | list | None
    ] = mapped_column(
        JSON,
        nullable=True,
    )

    output_data: Mapped[
        dict | list | None
    ] = mapped_column(
        JSON,
        nullable=True,
    )

    duration_ms: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    run: Mapped[
        "AgentRun"
    ] = relationship(
        "AgentRun",
        back_populates="steps",
    )