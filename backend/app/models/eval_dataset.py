from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin


class EvalDataset(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "eval_dataset"

    knowledge_base_id: Mapped[UUID] = mapped_column(
        ForeignKey("knowledge_base.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="v1",
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    cases: Mapped[list["EvalCase"]] = relationship(
        "EvalCase",
        back_populates="dataset",
        cascade="all, delete-orphan",
    )

    experiments: Mapped[list["EvalExperiment"]] = relationship(
        "EvalExperiment",
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
