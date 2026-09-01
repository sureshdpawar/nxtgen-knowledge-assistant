from datetime import (
    UTC,
    datetime,
)
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.llm_model_pricing_repository import (
    LLMModelPricingRepository,
)
from app.services.llm_cost_service import (
    PricingSnapshot,
)


class LLMPriceResolver:

    def __init__(
        self,
    ):
        self.repository = (
            LLMModelPricingRepository()
        )

    def resolve(
        self,
        db: Session,
        *,
        tenant_id: UUID,
        provider: str,
        model: str,
        effective_at: (
            datetime | None
        ) = None,
    ) -> (
        PricingSnapshot
        | None
    ):
        """
        Resolve configured pricing for one
        provider/model at request time.

        No provider or model is hard-coded.
        """

        effective_at = (
            effective_at
            or datetime.now(
                UTC
            )
        )

        pricing = (
            self.repository.resolve(
                db=db,
                tenant_id=
                    tenant_id,
                provider=
                    provider,
                model=
                    model,
                effective_at=
                    effective_at,
            )
        )

        if pricing is None:
            return None

        #
        # The current calculator supports
        # token-based pricing.
        #
        # Other pricing methods should not be
        # silently interpreted as token prices.
        #
        if (
            pricing.pricing_method
            != "token"
        ):
            return None

        if (
            pricing.input_rate
            is None
            or pricing.output_rate
            is None
            or pricing.unit_quantity
            is None
        ):
            return None

        if (
            pricing.unit_quantity
            < 1
        ):
            return None

        return PricingSnapshot(
            provider=
                pricing.provider,

            model=
                pricing.model,

            input_rate=
                pricing.input_rate,

            output_rate=
                pricing.output_rate,

            unit_tokens=
                pricing.unit_quantity,

            currency=
                pricing.currency,

            pricing_version=
                pricing.pricing_version,

            pricing_source=
                pricing.pricing_source,
        )