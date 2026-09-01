from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
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
    from app.models.tenant import Tenant


class LLMModelPricing(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    """
    Runtime-configured pricing for an LLM.

    Pricing is data, not application code.

    tenant_id = None
        platform/global catalog price

    tenant_id = <tenant>
        tenant-specific contracted price

    Multiple historical rows may exist for
    the same provider/model. Effective dates
    determine which price applies.
    """

    __tablename__ = (
        "llm_model_pricing"
    )

    tenant_id: Mapped[
        UUID | None
    ] = mapped_column(
        ForeignKey(
            "tenant.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    #
    # These are runtime values.
    #
    # No provider or model is assumed by
    # application code.
    #
    provider: Mapped[
        str
    ] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    model: Mapped[
        str
    ] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    #
    # Costing strategy.
    #
    # Initially Knowgentiq supports
    # token-based API pricing.
    #
    # Keeping this explicit allows future:
    #
    # - request
    # - duration
    # - infrastructure
    # - custom
    #
    pricing_method: Mapped[
        str
    ] = mapped_column(
        String(50),
        nullable=False,
        default="token",
        server_default="token",
        index=True,
    )

    #
    # Token pricing.
    #
    # Example unit_quantity:
    #
    # 1_000_000 tokens
    #
    # But this is configurable and therefore
    # not assumed by the cost calculator.
    #
    input_rate: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(
            precision=20,
            scale=10,
        ),
        nullable=True,
    )

    output_rate: Mapped[
        Decimal | None
    ] = mapped_column(
        Numeric(
            precision=20,
            scale=10,
        ),
        nullable=True,
    )

    unit_quantity: Mapped[
        int | None
    ] = mapped_column(
        Integer,
        nullable=True,
    )

    currency: Mapped[
        str
    ] = mapped_column(
        String(10),
        nullable=False,
        default="USD",
        server_default="USD",
    )

    #
    # Effective dating is critical.
    #
    # Historical requests should continue
    # using the price that was valid when
    # the request occurred.
    #
    effective_from: Mapped[
        datetime
    ] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=False,
        index=True,
    )

    effective_to: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(
            timezone=True
        ),
        nullable=True,
        index=True,
    )

    #
    # Audit/provenance.
    #
    pricing_version: Mapped[
        str | None
    ] = mapped_column(
        String(100),
        nullable=True,
    )

    pricing_source: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True,
    )

    #
    # Future costing methods can retain
    # additional provider/contract-specific
    # information without schema churn.
    #
    pricing_metadata: Mapped[
        dict
    ] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    is_active: Mapped[
        bool
    ] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True,
    )

    tenant: Mapped[
        "Tenant | None"
    ] = relationship(
        "Tenant",
    )