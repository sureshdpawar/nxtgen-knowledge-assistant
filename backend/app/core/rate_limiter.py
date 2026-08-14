import threading
import time

from collections import defaultdict
from collections import deque


class InMemoryRateLimiter:

    def __init__(self):
        self._requests: dict[
            str,
            deque[float],
        ] = defaultdict(deque)

        self._lock = (
            threading.Lock()
        )

    def check(
        self,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> int:
        """
        Check whether a request is allowed.

        Returns the number of remaining
        requests in the current window.

        Raises no exception itself.
        """

        now = time.monotonic()

        cutoff = (
            now - window_seconds
        )

        with self._lock:
            timestamps = (
                self._requests[key]
            )

            while (
                timestamps
                and timestamps[0]
                <= cutoff
            ):
                timestamps.popleft()

            if (
                len(timestamps)
                >= limit
            ):
                return -1

            timestamps.append(
                now
            )

            remaining = (
                limit
                - len(timestamps)
            )

            return remaining


rate_limiter = (
    InMemoryRateLimiter()
)