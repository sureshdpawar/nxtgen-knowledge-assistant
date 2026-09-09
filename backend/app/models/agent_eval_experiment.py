from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.agent_eval_dataset import AgentEvalDataset
    from app.models.agent_eval_result import AgentEvalResult


class AgentEvalExperiment(Base, UUIDMixin, TimestampMixin):
    """
    A dataset-based agent evaluation run.

    This is the persisted control-plane record that will later let staging or
    sandbox runs be compared over time. DeepEval remains the scoring engine;
    Knowgentiq owns experiment lifecycle, tenancy, persistence and comparison.
    """

    __tablename__ = "agent_eval_experiment"

    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenant.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    dataset_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_eval_dataset.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    agent_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
    )

    judge_model: Mapped[str | None] = mapped_column(String(255), nullable=True)

    pass_rate_threshold: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.80,
    )

    case_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    passed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    pass_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    outcome_correctness: Mapped[float | None] = mapped_column(Float, nullable=True)
    tool_correctness: Mapped[float | None] = mapped_column(Float, nullable=True)
    argument_correctness: Mapped[float | None] = mapped_column(Float, nullable=True)

    metrics: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    dataset: Mapped["AgentEvalDataset"] = relationship(
        "AgentEvalDataset",
        back_populates="experiments",
    )

    results: Mapped[list["AgentEvalResult"]] = relationship(
        "AgentEvalResult",
        back_populates="experiment",
        cascade="all, delete-orphan",
    )
