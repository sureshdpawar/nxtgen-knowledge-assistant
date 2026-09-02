from collections import defaultdict
from datetime import (
    date,
    datetime,
    time,
    timedelta,
    timezone,
)
from decimal import (
    Decimal,
    InvalidOperation,
)
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge_base import (
    KnowledgeBase,
)
from app.models.llm_usage_event import (
    LLMUsageEvent,
)


class CostAnalyticsService:
    """
    Aggregate persisted LLM usage and
    historical cost snapshots.

    Cost is NEVER recalculated using
    today's pricing.

    The source of truth for historical
    monetary cost is:

        llm_usage_event
        .usage_metadata["cost"]

    Unknown pricing remains unknown and is
    counted explicitly rather than treated
    as zero cost.
    """

    def get_analytics(
        self,
        db: Session,
        *,
        tenant_id: UUID,
        start_date: date,
        end_date: date,
        knowledge_base_id: (
            UUID | None
        ) = None,
        request_type: (
            str | None
        ) = None,
    ) -> dict:
        if end_date < start_date:
            raise ValueError(
                "end_date must be on or "
                "after start_date."
            )

        if (
            end_date - start_date
        ).days > 366:
            raise ValueError(
                "Date range cannot exceed "
                "367 days."
            )

        if (
            knowledge_base_id
            is not None
        ):
            self._validate_knowledge_base(
                db=db,
                tenant_id=tenant_id,
                knowledge_base_id=
                    knowledge_base_id,
            )

        start_at = datetime.combine(
            start_date,
            time.min,
            tzinfo=timezone.utc,
        )

        end_at = datetime.combine(
            end_date
            + timedelta(days=1),
            time.min,
            tzinfo=timezone.utc,
        )

        stmt = (
            select(
                LLMUsageEvent
            )
            .where(
                LLMUsageEvent.tenant_id
                == tenant_id,

                LLMUsageEvent.created_at
                >= start_at,

                LLMUsageEvent.created_at
                < end_at,
            )
            .order_by(
                LLMUsageEvent.created_at
                .asc()
            )
        )

        if (
            knowledge_base_id
            is not None
        ):
            stmt = stmt.where(
                LLMUsageEvent
                .knowledge_base_id
                == knowledge_base_id
            )

        normalized_request_type = (
            request_type.strip()
            if request_type
            else None
        )

        if normalized_request_type:
            stmt = stmt.where(
                LLMUsageEvent
                .request_type
                == normalized_request_type
            )

        events = list(
            db.scalars(
                stmt
            ).all()
        )

        knowledge_base_names = (
            self._knowledge_base_names(
                db=db,
                tenant_id=tenant_id,
                events=events,
            )
        )

        overview = (
            self._new_bucket()
        )

        daily = defaultdict(
            self._new_bucket
        )

        by_knowledge_base = (
            defaultdict(
                self._new_bucket
            )
        )

        by_model = defaultdict(
            self._new_bucket
        )

        by_workload = defaultdict(
            self._new_bucket
        )

        for event in events:
            cost = (
                self._extract_cost(
                    event
                )
            )

            self._add_event(
                overview,
                event,
                cost,
            )

            event_date = (
                self._event_date(
                    event
                )
            )

            self._add_event(
                daily[event_date],
                event,
                cost,
            )

            self._add_event(
                by_knowledge_base[
                    event.knowledge_base_id
                ],
                event,
                cost,
            )

            self._add_event(
                by_model[
                    (
                        event.provider,
                        event.model,
                    )
                ],
                event,
                cost,
            )

            self._add_event(
                by_workload[
                    event.request_type
                ],
                event,
                cost,
            )

        daily_rows = []

        current_date = start_date

        while current_date <= end_date:
            bucket = daily[
                current_date
            ]

            daily_rows.append({
                "date":
                    current_date,

                **self._serialize_bucket(
                    bucket,
                    include_input_output=True,
                ),
            })

            current_date += (
                timedelta(days=1)
            )

        kb_rows = []

        for (
            kb_id,
            bucket,
        ) in by_knowledge_base.items():
            kb_rows.append({
                "knowledge_base_id":
                    kb_id,

                "knowledge_base_name":
                    (
                        knowledge_base_names
                        .get(kb_id)
                        if kb_id
                        is not None
                        else None
                    ),

                **self._serialize_bucket(
                    bucket
                ),
            })

        kb_rows.sort(
            key=self._breakdown_sort_key
        )

        model_rows = []

        for (
            (
                provider,
                model,
            ),
            bucket,
        ) in by_model.items():
            model_rows.append({
                "provider":
                    provider,

                "model":
                    model,

                **self._serialize_bucket(
                    bucket
                ),
            })

        model_rows.sort(
            key=self._breakdown_sort_key
        )

        workload_rows = []

        for (
            workload,
            bucket,
        ) in by_workload.items():
            workload_rows.append({
                "request_type":
                    workload,

                **self._serialize_bucket(
                    bucket
                ),
            })

        workload_rows.sort(
            key=self._breakdown_sort_key
        )

        return {
            "start_date":
                start_date,

            "end_date":
                end_date,

            "timezone":
                "UTC",

            "knowledge_base_id":
                knowledge_base_id,

            "request_type":
                normalized_request_type,

            "overview":
                self._serialize_bucket(
                    overview,
                    include_input_output=True,
                ),

            "daily":
                daily_rows,

            "by_knowledge_base":
                kb_rows,

            "by_model":
                model_rows,

            "by_workload":
                workload_rows,
        }

    def _validate_knowledge_base(
        self,
        db: Session,
        *,
        tenant_id: UUID,
        knowledge_base_id: UUID,
    ) -> None:
        stmt = (
            select(
                KnowledgeBase.id
            )
            .where(
                KnowledgeBase.id
                == knowledge_base_id,

                KnowledgeBase.tenant_id
                == tenant_id,
            )
        )

        if (
            db.scalar(
                stmt
            )
            is None
        ):
            raise LookupError(
                "Knowledge base not found."
            )

    def _knowledge_base_names(
        self,
        db: Session,
        *,
        tenant_id: UUID,
        events: list[
            LLMUsageEvent
        ],
    ) -> dict:
        ids = {
            event.knowledge_base_id
            for event in events
            if event.knowledge_base_id
            is not None
        }

        if not ids:
            return {}

        stmt = (
            select(
                KnowledgeBase.id,
                KnowledgeBase.name,
            )
            .where(
                KnowledgeBase.tenant_id
                == tenant_id,

                KnowledgeBase.id.in_(
                    ids
                ),
            )
        )

        return {
            row[0]:
                row[1]
            for row in db.execute(
                stmt
            ).all()
        }

    def _event_date(
        self,
        event: LLMUsageEvent,
    ) -> date:
        created_at = (
            event.created_at
        )

        if created_at.tzinfo is None:
            created_at = (
                created_at.replace(
                    tzinfo=timezone.utc
                )
            )

        return (
            created_at
            .astimezone(
                timezone.utc
            )
            .date()
        )

    def _extract_cost(
        self,
        event: LLMUsageEvent,
    ) -> (
        tuple[
            str,
            Decimal,
        ]
        | None
    ):
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
            return None

        if (
            cost.get(
                "pricing_found"
            )
            is not True
        ):
            return None

        currency = cost.get(
            "currency"
        )

        total_cost = cost.get(
            "total_cost"
        )

        if (
            not currency
            or total_cost
            is None
        ):
            return None

        try:
            amount = Decimal(
                str(
                    total_cost
                )
            )
        except (
            InvalidOperation,
            ValueError,
            TypeError,
        ):
            return None

        return (
            str(
                currency
            ).upper(),
            amount,
        )

    def _new_bucket(
        self,
    ) -> dict:
        return {
            "request_count":
                0,

            "input_tokens":
                0,

            "output_tokens":
                0,

            "total_tokens":
                0,

            "costed_request_count":
                0,

            "uncosted_request_count":
                0,

            "costs":
                defaultdict(
                    Decimal
                ),
        }

    def _add_event(
        self,
        bucket: dict,
        event: LLMUsageEvent,
        cost: (
            tuple[
                str,
                Decimal,
            ]
            | None
        ),
    ) -> None:
        bucket[
            "request_count"
        ] += 1

        bucket[
            "input_tokens"
        ] += (
            event.input_tokens
            or 0
        )

        bucket[
            "output_tokens"
        ] += (
            event.output_tokens
            or 0
        )

        bucket[
            "total_tokens"
        ] += (
            event.total_tokens
            or 0
        )

        if cost is None:
            bucket[
                "uncosted_request_count"
            ] += 1
            return

        (
            currency,
            amount,
        ) = cost

        bucket[
            "costed_request_count"
        ] += 1

        bucket[
            "costs"
        ][
            currency
        ] += amount

    def _serialize_bucket(
        self,
        bucket: dict,
        *,
        include_input_output: bool = False,
    ) -> dict:
        result = {
            "request_count":
                bucket[
                    "request_count"
                ],

            "total_tokens":
                bucket[
                    "total_tokens"
                ],

            "costed_request_count":
                bucket[
                    "costed_request_count"
                ],

            "uncosted_request_count":
                bucket[
                    "uncosted_request_count"
                ],

            "cost_totals": [
                {
                    "currency":
                        currency,

                    "total_cost":
                        float(
                            amount
                        ),
                }
                for (
                    currency,
                    amount,
                ) in sorted(
                    bucket[
                        "costs"
                    ].items()
                )
            ],
        }

        if include_input_output:
            result[
                "input_tokens"
            ] = bucket[
                "input_tokens"
            ]

            result[
                "output_tokens"
            ] = bucket[
                "output_tokens"
            ]

        return result

    def _breakdown_sort_key(
        self,
        row: dict,
    ):
        total_cost = sum(
            item[
                "total_cost"
            ]
            for item in row[
                "cost_totals"
            ]
        )

        return (
            -total_cost,
            -row[
                "total_tokens"
            ],
            -row[
                "request_count"
            ],
        )
