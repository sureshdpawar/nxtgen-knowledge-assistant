from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    JSON,
    String,
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
    from app.models.conversation import Conversation
    from app.models.conversation_message import ConversationMessage
    from app.models.knowledge_base import KnowledgeBase
    from app.models.tenant import Tenant


class OnlineEvalResult(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    """
    A production RAG interaction selected for online quality evaluation.

    source_trace_id always refers to the original production request trace,
    not the later judge execution trace.
    """

    __tablename__ = "online_eval_result"

    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenant.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    knowledge_base_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("knowledge_base.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    conversation_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("conversation.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    message_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("conversation_message.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    source_trace_id: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="pending",
        server_default="pending",
        index=True,
    )

    sample_reason: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="random",
        server_default="random",
        index=True,
    )

    question: Mapped[str] = mapped_column(Text, nullable=False)
    actual_answer: Mapped[str] = mapped_column(Text, nullable=False)

    retrieval_context: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    generator_provider: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    generator_model: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    faithfulness_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    answer_relevancy_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    contextual_relevancy_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    passed: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        index=True,
    )

    evaluated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    evaluation_metadata: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    @property
    def evaluation_outcome(self) -> str | None:
        """
        API-facing outcome derived from persisted evaluation metadata.

        New rows:
        - pass
        - safe_abstention
        - fail

        Legacy completed rows fall back to the old passed boolean.
        Non-completed rows return None.
        """
        if self.status != "completed":
            return None

        metadata = self.evaluation_metadata or {}
        outcome = metadata.get("evaluation_outcome")

        if isinstance(outcome, str) and outcome.strip():
            return outcome.strip()

        if self.passed is True:
            return "pass"

        if self.passed is False:
            return "fail"

        return None

    tenant: Mapped["Tenant"] = relationship("Tenant")
    knowledge_base: Mapped["KnowledgeBase | None"] = relationship("KnowledgeBase")
    conversation: Mapped["Conversation | None"] = relationship("Conversation")
    message: Mapped["ConversationMessage | None"] = relationship("ConversationMessage")
