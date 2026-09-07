from decimal import Decimal
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

    def get_agent_run_usage(
        self,
        db: Session,
        *,
        tenant_id: UUID,
        run_id: UUID,
    ) -> dict:
        """
        Aggregate historical usage for one agent run.

        Cost is read from the persisted cost snapshot.
        It is never recalculated using today's prices.
        """

        events = (
            self.repository
            .list_for_agent_run(
                db=db,
                tenant_id=tenant_id,
                run_id=run_id,
            )
        )

        input_tokens = sum(
            event.input_tokens
            for event in events
        )

        output_tokens = sum(
            event.output_tokens
            for event in events
        )

        total_tokens = sum(
            event.total_tokens
            for event in events
        )

        total_cost = Decimal(
            "0"
        )

        currencies: set[str] = set()

        pricing_complete = (
            len(events) > 0
        )

        for event in events:
            metadata = (
                event.usage_metadata
                or {}
            )

            cost = metadata.get(
                "cost"
            )

            if not isinstance(
                cost,
                dict,
            ):
                pricing_complete = False
                continue

            if not cost.get(
                "pricing_found",
                False,
            ):
                pricing_complete = False
                continue

            event_cost = cost.get(
                "total_cost"
            )

            currency = cost.get(
                "currency"
            )

            if (
                event_cost is None
                or not currency
            ):
                pricing_complete = False
                continue

            try:
                total_cost += Decimal(
                    str(
                        event_cost
                    )
                )
            except (
                ValueError,
                TypeError,
            ):
                pricing_complete = False
                continue

            currencies.add(
                str(currency)
            )

        if len(
            currencies
        ) != 1:
            pricing_complete = False

        estimated_cost = (
            float(total_cost)
            if pricing_complete
            else None
        )

        currency = (
            next(
                iter(
                    currencies
                )
            )
            if pricing_complete
            else None
        )

        return {
            "request_count":
                len(events),

            "input_tokens":
                input_tokens,

            "output_tokens":
                output_tokens,

            "total_tokens":
                total_tokens,

            "estimated_cost":
                estimated_cost,

            "currency":
                currency,

            "pricing_complete":
                pricing_complete,
        }
