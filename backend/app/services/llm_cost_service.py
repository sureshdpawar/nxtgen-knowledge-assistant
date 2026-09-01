from dataclasses import (
    asdict,
    dataclass,
)
from decimal import Decimal


@dataclass(
    frozen=True
)
class PricingSnapshot:
    provider: str
    model: str

    input_rate: Decimal
    output_rate: Decimal

    unit_tokens: int

    currency: str

    pricing_version: (
        str | None
    ) = None

    pricing_source: (
        str | None
    ) = None


@dataclass(
    frozen=True
)
class LLMCostEstimate:
    provider: str
    model: str

    input_tokens: int
    output_tokens: int

    input_cost: (
        Decimal | None
    )

    output_cost: (
        Decimal | None
    )

    total_cost: (
        Decimal | None
    )

    currency: (
        str | None
    )

    pricing_version: (
        str | None
    )

    pricing_source: (
        str | None
    )

    pricing_found: bool

    pricing_snapshot: (
        dict | None
    )

    def to_dict(
        self,
    ) -> dict:
        data = asdict(
            self
        )

        for field_name in (
            "input_cost",
            "output_cost",
            "total_cost",
        ):
            value = data[
                field_name
            ]

            data[
                field_name
            ] = (
                float(value)
                if value is not None
                else None
            )

        snapshot = data.get(
            "pricing_snapshot"
        )

        if snapshot:
            for field_name in (
                "input_rate",
                "output_rate",
            ):
                value = snapshot.get(
                    field_name
                )

                if isinstance(
                    value,
                    Decimal,
                ):
                    snapshot[
                        field_name
                    ] = float(
                        value
                    )

        return data


class LLMCostService:
    """
    Provider-neutral cost calculator.

    This service knows HOW to calculate cost.

    It intentionally does NOT know:

    - provider price catalogs
    - model names
    - current market prices

    Pricing must be resolved externally and
    supplied as runtime configuration.
    """

    def estimate(
        self,
        *,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        pricing: (
            PricingSnapshot | None
        ),
    ) -> LLMCostEstimate:

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

        if pricing is None:
            return LLMCostEstimate(
                provider=
                    provider,
                model=
                    model,
                input_tokens=
                    input_tokens,
                output_tokens=
                    output_tokens,
                input_cost=
                    None,
                output_cost=
                    None,
                total_cost=
                    None,
                currency=
                    None,
                pricing_version=
                    None,
                pricing_source=
                    None,
                pricing_found=
                    False,
                pricing_snapshot=
                    None,
            )

        if pricing.unit_tokens < 1:
            raise ValueError(
                "pricing.unit_tokens must "
                "be greater than 0."
            )

        unit_tokens = Decimal(
            pricing.unit_tokens
        )

        input_cost = (
            Decimal(
                input_tokens
            )
            / unit_tokens
            * pricing.input_rate
        )

        output_cost = (
            Decimal(
                output_tokens
            )
            / unit_tokens
            * pricing.output_rate
        )

        total_cost = (
            input_cost
            + output_cost
        )

        return LLMCostEstimate(
            provider=
                provider,
            model=
                model,
            input_tokens=
                input_tokens,
            output_tokens=
                output_tokens,
            input_cost=
                input_cost,
            output_cost=
                output_cost,
            total_cost=
                total_cost,
            currency=
                pricing.currency,
            pricing_version=
                pricing.pricing_version,
            pricing_source=
                pricing.pricing_source,
            pricing_found=
                True,
            pricing_snapshot={
                "provider":
                    pricing.provider,

                "model":
                    pricing.model,

                "input_rate":
                    pricing.input_rate,

                "output_rate":
                    pricing.output_rate,

                "unit_tokens":
                    pricing.unit_tokens,

                "currency":
                    pricing.currency,

                "pricing_version":
                    pricing.pricing_version,

                "pricing_source":
                    pricing.pricing_source,
            },
        )