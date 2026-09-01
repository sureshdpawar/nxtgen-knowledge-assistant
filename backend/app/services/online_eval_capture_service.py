import random

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.telemetry import (
    get_current_trace_id,
)
from app.models.online_eval_result import (
    OnlineEvalResult,
)
from app.repositories.online_eval_result_repository import (
    OnlineEvalResultRepository,
)


class OnlineEvalCaptureService:
    """
    Lightweight request-path capture for
    production online evaluation.

    This service does NOT run evaluators or
    make any LLM calls. It only decides whether
    an interaction should be sampled and, when
    selected, persists a pending evaluation row.

    Actual evaluation is performed later by
    OnlineEvalService.
    """

    def __init__(self):
        self.repository = (
            OnlineEvalResultRepository()
        )

    def should_sample(
        self,
        *,
        sample_rate: float,
        force: bool = False,
    ) -> bool:
        """
        Return whether the production interaction
        should be captured for later evaluation.

        sample_rate must be between 0.0 and 1.0.
        """

        if (
            sample_rate < 0.0
            or sample_rate > 1.0
        ):
            raise ValueError(
                "Online evaluation sample_rate "
                "must be between 0.0 and 1.0."
            )

        if force:
            return True

        if sample_rate == 0.0:
            return False

        if sample_rate == 1.0:
            return True

        return (
            random.random()
            < sample_rate
        )

    def capture(
        self,
        db: Session,
        *,
        tenant_id: UUID,
        knowledge_base_id: (
            UUID | None
        ),
        conversation_id: (
            UUID | None
        ),
        message_id: (
            UUID | None
        ),
        question: str,
        actual_answer: str,
        retrieval_context: list[str],
        generator_provider: (
            str | None
        ) = None,
        generator_model: (
            str | None
        ) = None,
        sample_reason: str = "random",
        source_trace_id: (
            str | None
        ) = None,
        evaluation_metadata: (
            dict | None
        ) = None,
    ) -> OnlineEvalResult | None:
        """
        Persist a sampled production interaction.

        source_trace_id always represents the
        original user-facing production request.

        If source_trace_id is not supplied, the
        current OpenTelemetry trace is used.

        The caller owns the transaction and commit.
        """

        resolved_trace_id = (
            source_trace_id
            or get_current_trace_id()
        )

        if not resolved_trace_id:
            return None

        normalized_question = (
            question.strip()
        )

        normalized_answer = (
            actual_answer.strip()
        )

        if not normalized_question:
            raise ValueError(
                "Online evaluation question "
                "cannot be empty."
            )

        if not normalized_answer:
            raise ValueError(
                "Online evaluation actual_answer "
                "cannot be empty."
            )

        contexts = [
            str(context)
            for context
            in (
                retrieval_context
                or []
            )
            if str(context).strip()
        ]

        result = OnlineEvalResult(
            tenant_id=
                tenant_id,

            knowledge_base_id=
                knowledge_base_id,

            conversation_id=
                conversation_id,

            message_id=
                message_id,

            source_trace_id=
                resolved_trace_id,

            status=
                "pending",

            sample_reason=
                sample_reason,

            question=
                normalized_question,

            actual_answer=
                normalized_answer,

            retrieval_context=
                contexts,

            generator_provider=
                generator_provider,

            generator_model=
                generator_model,

            evaluation_metadata=
                evaluation_metadata
                or {},
        )

        return (
            self.repository.create(
                db=db,
                obj=result,
            )
        )
