from datetime import date
from uuid import UUID

from pydantic import BaseModel


class CurrencyCostTotal(BaseModel):
    currency: str
    total_cost: float


class CostAnalyticsOverview(BaseModel):
    request_count: int
    input_tokens: int
    output_tokens: int
    total_tokens: int

    costed_request_count: int
    uncosted_request_count: int

    cost_totals: list[
        CurrencyCostTotal
    ]


class CostAnalyticsDailyPoint(BaseModel):
    date: date

    request_count: int
    input_tokens: int
    output_tokens: int
    total_tokens: int

    costed_request_count: int
    uncosted_request_count: int

    cost_totals: list[
        CurrencyCostTotal
    ]


class CostAnalyticsKnowledgeBaseBreakdown(
    BaseModel
):
    knowledge_base_id: UUID | None
    knowledge_base_name: str | None

    request_count: int
    total_tokens: int

    costed_request_count: int
    uncosted_request_count: int

    cost_totals: list[
        CurrencyCostTotal
    ]


class CostAnalyticsModelBreakdown(
    BaseModel
):
    provider: str
    model: str

    request_count: int
    total_tokens: int

    costed_request_count: int
    uncosted_request_count: int

    cost_totals: list[
        CurrencyCostTotal
    ]


class CostAnalyticsWorkloadBreakdown(
    BaseModel
):
    request_type: str

    request_count: int
    total_tokens: int

    costed_request_count: int
    uncosted_request_count: int

    cost_totals: list[
        CurrencyCostTotal
    ]


class CostAnalyticsResponse(BaseModel):
    start_date: date
    end_date: date
    timezone: str

    knowledge_base_id: UUID | None
    request_type: str | None

    overview: CostAnalyticsOverview

    daily: list[
        CostAnalyticsDailyPoint
    ]

    by_knowledge_base: list[
        CostAnalyticsKnowledgeBaseBreakdown
    ]

    by_model: list[
        CostAnalyticsModelBreakdown
    ]

    by_workload: list[
        CostAnalyticsWorkloadBreakdown
    ]
