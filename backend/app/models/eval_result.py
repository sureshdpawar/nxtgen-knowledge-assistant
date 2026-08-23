from uuid import UUID

from sqlalchemy import Boolean, Float, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin


class EvalResult(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "eval_result"

    experiment_id: Mapped[UUID] = mapped_column(
        ForeignKey("eval_experiment.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    eval_case_id: Mapped[UUID] = mapped_column(
        ForeignKey("eval_case.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    retrieved_document_ids: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    retrieved_chunk_ids: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    retrieved_distances: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    expected_rank: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    hit_at_k: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    reciprocal_rank: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    experiment: Mapped["EvalExperiment"] = relationship(
        "EvalExperiment",
        back_populates="results",
    )

    eval_case: Mapped["EvalCase"] = relationship(
        "EvalCase",
        back_populates="results",
    )
