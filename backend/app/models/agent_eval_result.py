from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, Float, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.agent_eval_case import AgentEvalCase
    from app.models.agent_eval_experiment import AgentEvalExperiment


class AgentEvalResult(Base, UUIDMixin, TimestampMixin):
    """
    Per-case result for one AgentEvalExperiment.

    agent_run_id links the evaluation result to the real Knowgentiq AgentRun
    and therefore to its persisted AgentRunSteps/tool trace.
    """

    __tablename__ = "agent_eval_result"

    experiment_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_eval_experiment.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    eval_case_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_eval_case.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    agent_run_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("agent_run.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    actual_answer: Mapped[str | None] = mapped_column(Text, nullable=True)

    tools_called: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    outcome_correctness: Mapped[float | None] = mapped_column(Float, nullable=True)
    tool_correctness: Mapped[float | None] = mapped_column(Float, nullable=True)
    argument_correctness: Mapped[float | None] = mapped_column(Float, nullable=True)

    forbidden_tool_violations: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    metrics: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    judge_metadata: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    experiment: Mapped["AgentEvalExperiment"] = relationship(
        "AgentEvalExperiment",
        back_populates="results",
    )

    eval_case: Mapped["AgentEvalCase"] = relationship(
        "AgentEvalCase",
        back_populates="results",
    )
