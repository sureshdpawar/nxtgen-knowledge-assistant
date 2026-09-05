from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    ForeignKey,
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
    from app.models.eval_dataset import (
        EvalDataset,
    )
    from app.models.eval_result import (
        EvalResult,
    )


class EvalCase(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "eval_case"

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

    question: Mapped[
        str
    ] = mapped_column(
        Text,
        nullable=False,
    )

    #
    # Optional provenance for golden cases
    # promoted from completed agent runs.
    #
    # SET NULL preserves the eval case if
    # runtime history is later deleted.
    #
    source_agent_run_id: Mapped[
        UUID | None
    ] = mapped_column(
        ForeignKey(
            "agent_run.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        unique=True,
        index=True,
    )

    #
    # Immutable-at-promotion snapshot of
    # useful runtime context. The promoted
    # golden case itself remains independent
    # from future runtime changes.
    #
    source_metadata: Mapped[
        dict
    ] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    #
    # Environment-specific ground truth.
    #
    # Useful when a golden dataset is created
    # directly against one KB/database.
    #
    expected_document_id: Mapped[
        UUID | None
    ] = mapped_column(
        ForeignKey(
            "document.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    expected_chunk_id: Mapped[
        UUID | None
    ] = mapped_column(
        ForeignKey(
            "document_chunk.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    #
    # Portable source ground truth.
    #
    # Example:
    #
    # [
    #     {
    #         "type": "url",
    #         "value":
    #           "https://nxtgeninnovate.com/"
    #           "ai-data-science-solutions.html"
    #     }
    # ]
    #
    # This allows the same golden dataset
    # to work across dev/staging/prod even
    # when document UUIDs are different.
    #
    expected_sources: Mapped[
        list
    ] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    expected_text: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    expected_answer: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    answerable: Mapped[
        bool
    ] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    dataset: Mapped[
        "EvalDataset"
    ] = relationship(
        "EvalDataset",
        back_populates="cases",
    )

    results: Mapped[
        list["EvalResult"]
    ] = relationship(
        "EvalResult",
        back_populates="eval_case",
        cascade="all, delete-orphan",
    )
