from pydantic import BaseModel


class UsageMetricStatus(
    BaseModel
):
    used: int

    limit: (
        int | None
    )

    remaining: (
        int | None
    )

    percentage_used: (
        float | None
    )


class UsagePeriodStatus(
    BaseModel
):
    messages: UsageMetricStatus

    input_tokens: UsageMetricStatus

    output_tokens: UsageMetricStatus

    total_tokens: UsageMetricStatus

    reset_at: str


class UsageScopeStatus(
    BaseModel
):
    scope: str

    enabled: bool

    timezone: str

    daily: UsagePeriodStatus

    monthly: UsagePeriodStatus


class UsageStatusResponse(
    BaseModel
):
    allowed: bool

    scopes: list[
        UsageScopeStatus
    ]