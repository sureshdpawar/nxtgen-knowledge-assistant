from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    case,
    or_,
    select,
)
from sqlalchemy.orm import Session

from app.models.llm_model_pricing import (
    LLMModelPricing,
)
from app.repositories.base_repository import (
    BaseRepository,
)


class LLMModelPricingRepository(
    BaseRepository[
        LLMModelPricing
    ],
):

    def __init__(
        self,
    ):
        super().__init__(
            LLMModelPricing,
        )

    def resolve(
        self,
        db: Session,
        *,
        tenant_id: UUID,
        provider: str,
        model: str,
        effective_at: datetime,
    ) -> (
        LLMModelPricing
        | None
    ):
        """
        Resolve the price applicable at a
        specific point in time.

        Precedence:

        1. tenant-specific price
        2. platform/global price

        Within the same precedence level,
        the most recently effective price wins.
        """

        tenant_priority = case(
            (
                LLMModelPricing
                .tenant_id
                == tenant_id,
                0,
            ),
            else_=1,
        )

        stmt = (
            select(
                LLMModelPricing
            )
            .where(
                LLMModelPricing
                .provider
                == provider,

                LLMModelPricing
                .model
                == model,

                LLMModelPricing
                .is_active
                .is_(True),

                or_(
                    LLMModelPricing
                    .tenant_id
                    == tenant_id,

                    LLMModelPricing
                    .tenant_id
                    .is_(None),
                ),

                LLMModelPricing
                .effective_from
                <= effective_at,

                or_(
                    LLMModelPricing
                    .effective_to
                    .is_(None),

                    LLMModelPricing
                    .effective_to
                    > effective_at,
                ),
            )
            .order_by(
                tenant_priority,
                LLMModelPricing
                .effective_from
                .desc(),
                LLMModelPricing
                .created_at
                .desc(),
            )
            .limit(
                1
            )
        )

        return db.scalar(
            stmt
        )