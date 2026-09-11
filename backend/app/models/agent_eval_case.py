from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.agent_eval_dataset import AgentEvalDataset
    from app.models.agent_eval_result import AgentEvalResult


class AgentEvalCase(Base, UUIDMixin, TimestampMixin):
    """
    One reusable business scenario in an agent regression dataset.

    expected_tools is optional. This allows business users to provide only
    input + expected outcome, while technical users can add exact tool and
    argument expectations.

    forbidden_tools is deterministic guardrail evidence: if any listed tool is
    actually executed, the case fails regardless of LLM-judge scores.

    source_agent_run_id allows a real production/staging run to be promoted
    into the regression dataset later without losing provenance.
    """

    __tablename__ = "agent_eval_case"

    dataset_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_eval_dataset.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    input: Mapped[str] = mapped_column(Text, nullable=False)
    expected_outcome: Mapped[str] = mapped_column(Text, nullable=False)

    expected_tools: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    forbidden_tools: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    source_agent_run_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("agent_run.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    dataset: Mapped["AgentEvalDataset"] = relationship(
        "AgentEvalDataset",
        back_populates="cases",
    )

    results: Mapped[list["AgentEvalResult"]] = relationship(
        "AgentEvalResult",
        back_populates="eval_case",
        cascade="all, delete-orphan",
    )
