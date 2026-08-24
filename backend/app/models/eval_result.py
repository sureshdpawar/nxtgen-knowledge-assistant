from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    Float,
    ForeignKey,
    Integer,
    JSON,
    Text,
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
    from app.models.eval_case import (
        EvalCase,
    )
    from app.models.eval_experiment import (
        EvalExperiment,
    )


class EvalResult(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "eval_result"

    experiment_id: Mapped[
        UUID
    ] = mapped_column(
        ForeignKey(
            "eval_experiment.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    eval_case_id: Mapped[
        UUID
    ] = mapped_column(
        ForeignKey(
            "eval_case.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    retrieved_document_ids: Mapped[
        list
    ] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    retrieved_chunk_ids: Mapped[
        list
    ] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    retrieved_distances: Mapped[
        list
    ] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    retrieval_context: Mapped[
        list
    ] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    expected_rank: Mapped[
        int | None
    ] = mapped_column(
        Integer,
        nullable=True,
    )

    hit_at_k: Mapped[
        bool | None
    ] = mapped_column(
        Boolean,
        nullable=True,
    )

    reciprocal_rank: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    actual_answer: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    correctness_score: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    faithfulness_score: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    relevancy_score: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    refusal_score: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    passed: Mapped[
        bool | None
    ] = mapped_column(
        Boolean,
        nullable=True,
    )

    metrics: Mapped[
        dict
    ] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    judge_metadata: Mapped[
        dict
    ] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    experiment: Mapped[
        "EvalExperiment"
    ] = relationship(
        "EvalExperiment",
        back_populates="results",
    )

    eval_case: Mapped[
        "EvalCase"
    ] = relationship(
        "EvalCase",
        back_populates="results",
    )