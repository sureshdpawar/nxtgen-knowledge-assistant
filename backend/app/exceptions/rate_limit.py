from app.exceptions.base import (
    AppException,
)


class RateLimitExceededError(
    AppException,
):

    def __init__(
        self,
        retry_after: int = 60,
    ):
        self.retry_after = (
            retry_after
        )

        super().__init__(
            status_code=429,
            error_code=
                "RATE_LIMIT_EXCEEDED",
            message=(
                "Too many requests. "
                "Please try again shortly."
            ),
        )