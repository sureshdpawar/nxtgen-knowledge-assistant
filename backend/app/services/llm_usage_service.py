from uuid import UUID

from sqlalchemy.orm import Session

from app.core.telemetry import (
    get_current_trace_id,
)
from app.models.llm_usage_event import (
    LLMUsageEvent,
)
from app.repositories.llm_usage_event_repository import (
    LLMUsageEventRepository,
)
from app.services.llm_cost_service import (
    LLMCostService,
)
from app.services.llm_pricing_service import (
    LLMPriceResolver,
)


class LLMUsageService:

    def __init__(
        self,
    ):
        self.repository = (
            LLMUsageEventRepository()
        )

        self.price_resolver = (
            LLMPriceResolver()
        )

        self.cost_service = (
            LLMCostService()
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

        #
        # Resolve pricing dynamically from DB.
        #
        pricing = (
            self.price_resolver.resolve(
                db=db,

                tenant_id=
                    tenant_id,

                provider=
                    provider,

                model=
                    model,
            )
        )

        #
        # Calculate cost only from the
        # resolved pricing snapshot.
        #
        cost_estimate = (
            self.cost_service.estimate(
                provider=
                    provider,

                model=
                    model,

                input_tokens=
                    input_tokens,

                output_tokens=
                    output_tokens,

                pricing=
                    pricing,
            )
        )

        metadata = dict(
            usage_metadata
            or {}
        )

        #
        # Correlate financial usage with
        # the execution trace.
        #
        metadata[
            "trace_id"
        ] = get_current_trace_id()

        #
        # Persist the result AND the exact
        # pricing snapshot used.
        #
        # Historical reports therefore do not
        # need to recalculate old requests
        # using today's prices.
        #
        metadata[
            "cost"
        ] = (
            cost_estimate.to_dict()
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
                metadata,
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
        # Keep usage atomic with the parent
        # chat/agent/evaluation transaction.
        #
        return event