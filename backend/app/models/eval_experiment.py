from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
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

from app.db.base import Base
from app.db.mixins import (
    TimestampMixin,
    UUIDMixin,
)

if TYPE_CHECKING:
    from app.models.eval_dataset import (
        EvalDataset,
    )
    from app.models.eval_result import (
        EvalResult,
    )


class EvalExperiment(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "eval_experiment"

    dataset_id: Mapped[
        UUID
    ] = mapped_column(
        ForeignKey(
            "eval_dataset.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    knowledge_base_id: Mapped[
        UUID
    ] = mapped_column(
        ForeignKey(
            "knowledge_base.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    name: Mapped[
        str
    ] = mapped_column(
        String(255),
        nullable=False,
    )

    eval_type: Mapped[
        str
    ] = mapped_column(
        String(50),
        nullable=False,
        default="retrieval",
    )

    top_k: Mapped[
        int
    ] = mapped_column(
        Integer,
        nullable=False,
    )

    chunk_size: Mapped[
        int | None
    ] = mapped_column(
        Integer,
        nullable=True,
    )

    chunk_overlap: Mapped[
        int | None
    ] = mapped_column(
        Integer,
        nullable=True,
    )

    embedding_model: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True,
    )

    llm_model: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True,
    )

    status: Mapped[
        str
    ] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
    )

    hit_rate: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    mrr: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    metrics: Mapped[
        dict
    ] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    dataset: Mapped[
        "EvalDataset"
    ] = relationship(
        "EvalDataset",
        back_populates="experiments",
    )

    results: Mapped[
        list["EvalResult"]
    ] = relationship(
        "EvalResult",
        back_populates="experiment",
        cascade="all, delete-orphan",
    )