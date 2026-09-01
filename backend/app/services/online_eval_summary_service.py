from collections import Counter
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.online_eval_result import (
    OnlineEvalResult,
)
from app.repositories.online_eval_result_repository import (
    OnlineEvalResultRepository,
)


class OnlineEvalSummaryService:
    """
    Read-only aggregation service for production
    online evaluation.

    Cost data is derived from each row's persisted
    evaluation_metadata["judge_cost"] snapshot.
    Unknown pricing is never converted to zero.
    """

    def __init__(self):
        self.repository = (
            OnlineEvalResultRepository()
        )

    @staticmethod
    def _average(
        values: list[
            float
        ],
    ) -> float | None:
        if not values:
            return None

        return (
            sum(values)
            / len(values)
        )

    @staticmethod
    def _score_values(
        rows: list[
            OnlineEvalResult
        ],
        attribute_name: str,
    ) -> list[
        float
    ]:
        values: list[
            float
        ] = []

        for row in rows:
            value = getattr(
                row,
                attribute_name,
                None,
            )

            if value is None:
                continue

            values.append(
                float(value)
            )

        return values

    @staticmethod
    def _cost_summary(
        rows: list[
            OnlineEvalResult
        ],
    ) -> dict:
        priced_totals: list[
            tuple[
                float,
                str,
            ]
        ] = []

        priced_evaluations = 0
        unpriced_evaluations = 0

        for row in rows:
            if row.status != "completed":
                continue

            metadata = (
                row.evaluation_metadata
                or {}
            )

            judge_cost = (
                metadata.get(
                    "judge_cost"
                )
                or {}
            )

            total = judge_cost.get(
                "total"
            )

            currency = judge_cost.get(
                "currency"
            )

            pricing_complete = bool(
                judge_cost.get(
                    "pricing_complete",
                    False,
                )
            )

            if (
                total is None
                or currency is None
            ):
                unpriced_evaluations += 1
                continue

            try:
                numeric_total = float(
                    total
                )
            except (
                TypeError,
                ValueError,
            ):
                unpriced_evaluations += 1
                continue

            priced_evaluations += 1

            if not pricing_complete:
                unpriced_evaluations += 1

            priced_totals.append(
                (
                    numeric_total,
                    str(currency),
                )
            )

        if not priced_totals:
            return {
                "total":
                    None,
                "currency":
                    None,
                "priced_evaluations":
                    priced_evaluations,
                "unpriced_evaluations":
                    unpriced_evaluations,
                "pricing_complete":
                    (
                        unpriced_evaluations
                        == 0
                    ),
            }

        currencies = {
            currency
            for _, currency
            in priced_totals
        }

        if len(currencies) != 1:
            return {
                "total":
                    None,
                "currency":
                    None,
                "priced_evaluations":
                    priced_evaluations,
                "unpriced_evaluations":
                    unpriced_evaluations,
                "pricing_complete":
                    False,
            }

        currency = next(
            iter(
                currencies
            )
        )

        return {
            "total":
                sum(
                    value
                    for value, _
                    in priced_totals
                ),
            "currency":
                currency,
            "priced_evaluations":
                priced_evaluations,
            "unpriced_evaluations":
                unpriced_evaluations,
            "pricing_complete":
                (
                    unpriced_evaluations
                    == 0
                ),
        }

    def get_summary(
        self,
        db: Session,
        *,
        tenant_id: UUID,
        knowledge_base_id: (
            UUID | None
        ) = None,
        generator_provider: (
            str | None
        ) = None,
        generator_model: (
            str | None
        ) = None,
        created_from: (
            datetime | None
        ) = None,
        created_to: (
            datetime | None
        ) = None,
    ) -> dict:
        rows = (
            self.repository
            .list_for_summary(
                db=db,
                tenant_id=
                    tenant_id,
                knowledge_base_id=
                    knowledge_base_id,
                generator_provider=
                    generator_provider,
                generator_model=
                    generator_model,
                created_from=
                    created_from,
                created_to=
                    created_to,
            )
        )

        counts = Counter(
            row.status
            for row
            in rows
        )

        completed_rows = [
            row
            for row
            in rows
            if row.status
            == "completed"
        ]

        passed_count = sum(
            1
            for row
            in completed_rows
            if row.passed is True
        )

        not_passed_count = sum(
            1
            for row
            in completed_rows
            if row.passed is False
        )

        pass_denominator = (
            passed_count
            + not_passed_count
        )

        pass_rate = (
            passed_count
            / pass_denominator
            if pass_denominator
            else None
        )

        return {
            "total":
                len(rows),

            "pending":
                counts.get(
                    "pending",
                    0,
                ),

            "running":
                counts.get(
                    "running",
                    0,
                ),

            "completed":
                counts.get(
                    "completed",
                    0,
                ),

            "failed":
                counts.get(
                    "failed",
                    0,
                ),

            "passed":
                passed_count,

            "not_passed":
                not_passed_count,

            "pass_rate":
                pass_rate,

            "average_scores": {
                "faithfulness":
                    self._average(
                        self._score_values(
                            completed_rows,
                            "faithfulness_score",
                        )
                    ),

                "answer_relevancy":
                    self._average(
                        self._score_values(
                            completed_rows,
                            "answer_relevancy_score",
                        )
                    ),

                "contextual_relevancy":
                    self._average(
                        self._score_values(
                            completed_rows,
                            "contextual_relevancy_score",
                        )
                    ),
            },

            "evaluation_cost":
                self._cost_summary(
                    completed_rows
                ),
        }
