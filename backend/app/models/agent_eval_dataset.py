from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.agent import Agent
    from app.models.agent_eval_case import AgentEvalCase
    from app.models.agent_eval_experiment import AgentEvalExperiment


class AgentEvalDataset(Base, UUIDMixin, TimestampMixin):
    """
    Curated agent regression dataset.

    Kept separate from the existing RAG EvalDataset because RAG datasets are
    knowledge-base scoped while agent datasets are agent scoped and carry
    tool/action expectations.
    """

    __tablename__ = "agent_eval_dataset"

    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenant.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    agent_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="v1")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    agent: Mapped["Agent"] = relationship("Agent")

    cases: Mapped[list["AgentEvalCase"]] = relationship(
        "AgentEvalCase",
        back_populates="dataset",
        cascade="all, delete-orphan",
    )

    experiments: Mapped[list["AgentEvalExperiment"]] = relationship(
        "AgentEvalExperiment",
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
