from fastapi import (
    Depends,
)

from app.auth.dependencies import (
    get_current_active_user,
)
from app.core.rate_limiter import (
    rate_limiter,
)
from app.exceptions.rate_limit import (
    RateLimitExceededError,
)
from app.models.user import User


CHAT_RATE_LIMIT = 20

SEARCH_RATE_LIMIT = 60

RATE_LIMIT_WINDOW_SECONDS = 60


def _check_rate_limit(
    user: User,
    bucket: str,
    limit: int,
) -> None:

    key = (
        f"user:{user.id}:"
        f"{bucket}"
    )

    remaining = (
        rate_limiter.check(
            key=key,
            limit=limit,
            window_seconds=
                RATE_LIMIT_WINDOW_SECONDS,
        )
    )

    if remaining < 0:
        raise RateLimitExceededError(
            retry_after=
                RATE_LIMIT_WINDOW_SECONDS,
        )


def enforce_chat_rate_limit(
    current_user: User = Depends(
        get_current_active_user,
    ),
) -> User:

    _check_rate_limit(
        user=current_user,
        bucket="chat",
        limit=CHAT_RATE_LIMIT,
    )

    return current_user


def enforce_search_rate_limit(
    current_user: User = Depends(
        get_current_active_user,
    ),
) -> User:

    _check_rate_limit(
        user=current_user,
        bucket="search",
        limit=SEARCH_RATE_LIMIT,
    )

    return current_user