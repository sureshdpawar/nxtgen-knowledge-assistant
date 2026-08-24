class UsageQuotaExceededError(Exception):

    def __init__(
        self,
        message: str,
        *,
        scope: str,
        period: str | None = None,
        metric: str | None = None,
        limit: int | None = None,
        used: int | None = None,
        reset_at: str | None = None,
    ):
        super().__init__(
            message
        )

        self.message = message
        self.scope = scope
        self.period = period
        self.metric = metric
        self.limit = limit
        self.used = used
        self.reset_at = reset_at

    def to_dict(
        self,
    ) -> dict:
        return {
            "error":
                "usage_limit_reached",

            "message":
                self.message,

            "scope":
                self.scope,

            "period":
                self.period,

            "metric":
                self.metric,

            "limit":
                self.limit,

            "used":
                self.used,

            "reset_at":
                self.reset_at,
        }