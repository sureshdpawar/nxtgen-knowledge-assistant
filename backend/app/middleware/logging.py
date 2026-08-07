import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("nxtgen.request")


class LoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        start = time.perf_counter()

        response = await call_next(request)

        duration = (time.perf_counter() - start) * 1000

        request_id = request.state.request_id

        error_code = getattr(
            request.state,
            "error_code",
            None,
        )

        error_message = getattr(
            request.state,
            "error_message",
            None,
        )

        log_message = (
            "[%s] %s %s %s %.2f ms"
            % (
                request_id,
                request.method,
                request.url.path,
                response.status_code,
                duration,
            )
        )

        if error_code:
            log_message = (
                "[%s] %s %s %s %s \"%s\" %.2f ms"
                % (
                    request_id,
                    request.method,
                    request.url.path,
                    response.status_code,
                    error_code,
                    error_message,
                    duration,
                )
            )

        if response.status_code >= 500:
            logger.error(log_message)

        elif response.status_code >= 400:
            logger.warning(log_message)

        else:
            logger.info(log_message)

        return response