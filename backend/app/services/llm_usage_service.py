from uuid import UUID

from sqlalchemy.orm import Session

from app.models.llm_usage_event import (
    LLMUsageEvent,
)
from app.repositories.llm_usage_event_repository import (
    LLMUsageEventRepository,
)


class LLMUsageService:

    def __init__(self):
        self.repository = (
            LLMUsageEventRepository()
        )

    def record(
        self,
        db: Session,
        *,
        tenant_id: UUID,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        knowledge_base_id: (
            UUID | None
        ) = None,
        chat_channel_id: (
            UUID | None
        ) = None,
        conversation_id: (
            UUID | None
        ) = None,
        message_id: (
            UUID | None
        ) = None,
        request_type: str = "chat",
        usage_metadata: (
            dict | None
        ) = None,
    ) -> LLMUsageEvent:
        if input_tokens < 0:
            raise ValueError(
                "input_tokens cannot "
                "be negative."
            )

        if output_tokens < 0:
            raise ValueError(
                "output_tokens cannot "
                "be negative."
            )

        total_tokens = (
            input_tokens
            + output_tokens
        )

        event = LLMUsageEvent(
            tenant_id=
                tenant_id,
            knowledge_base_id=
                knowledge_base_id,
            chat_channel_id=
                chat_channel_id,
            conversation_id=
                conversation_id,
            message_id=
                message_id,
            provider=
                provider,
            model=
                model,
            request_type=
                request_type,
            input_tokens=
                input_tokens,
            output_tokens=
                output_tokens,
            total_tokens=
                total_tokens,
            usage_metadata=
                usage_metadata
                or {},
        )

        event = (
            self.repository.create(
                db=db,
                entity=event,
            )
        )

        #
        # Do not commit here.
        #
        # Usage should normally be committed
        # atomically with the assistant
        # message/chat transaction.
        #
        return event