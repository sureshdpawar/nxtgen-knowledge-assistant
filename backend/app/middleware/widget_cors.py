from collections.abc import Awaitable, Callable

from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp


class WidgetCORSMiddleware:
    """
    CORS handling specifically for the public Website Widget API.

    This middleware handles browser CORS mechanics only.

    It does NOT authorize an origin.

    Actual Website-channel authorization still happens inside
    WebsiteChannelSessionService.validate_origin(), which checks
    ChatChannel.configuration["allowed_origins"].

    This distinction is important:

    CORS:
        Allows a browser to make the HTTP request.

    Channel origin validation:
        Decides whether that website is authorized to use
        the configured Website channel.
    """

    WIDGET_PATH_PREFIX = (
        "/public/v1/widget"
    )

    def __init__(
        self,
        app: ASGIApp,
    ):
        self.app = app

    async def __call__(
        self,
        scope,
        receive,
        send,
    ):
        if (
            scope["type"]
            != "http"
        ):
            await self.app(
                scope,
                receive,
                send,
            )
            return

        request = Request(
            scope,
            receive=receive,
        )

        if not request.url.path.startswith(
            self.WIDGET_PATH_PREFIX
        ):
            await self.app(
                scope,
                receive,
                send,
            )
            return

        origin = request.headers.get(
            "origin"
        )

        #
        # Non-browser/server-to-server requests may not
        # contain an Origin header.
        #
        # We do not need to add CORS headers in that case.
        #
        if not origin:
            await self.app(
                scope,
                receive,
                send,
            )
            return

        #
        # Browser CORS preflight.
        #
        # We deliberately allow the browser to perform
        # the actual request.
        #
        # The actual widget endpoint then validates
        # `origin` against the Website ChatChannel's
        # allowed_origins configuration.
        #
        if (
            request.method.upper()
            == "OPTIONS"
        ):
            response = Response(
                status_code=204,
            )

            self._add_cors_headers(
                response=response,
                origin=origin,
                request=request,
            )

            await response(
                scope,
                receive,
                send,
            )

            return

        #
        # Actual request.
        #
        # Wrap `send` so CORS headers are added to
        # both successful responses and 4xx/5xx responses.
        #
        async def send_with_cors(
            message,
        ):
            if (
                message["type"]
                == "http.response.start"
            ):
                headers = list(
                    message.get(
                        "headers",
                        [],
                    )
                )

                headers.extend(
                    self._cors_headers(
                        origin=origin,
                        request=request,
                    )
                )

                message[
                    "headers"
                ] = headers

            await send(
                message
            )

        await self.app(
            scope,
            receive,
            send_with_cors,
        )

    def _add_cors_headers(
        self,
        response: Response,
        origin: str,
        request: Request,
    ) -> None:
        response.headers[
            "Access-Control-Allow-Origin"
        ] = origin

        response.headers[
            "Vary"
        ] = "Origin"

        response.headers[
            "Access-Control-Allow-Methods"
        ] = (
            "GET, POST, OPTIONS"
        )

        response.headers[
            "Access-Control-Allow-Headers"
        ] = (
            "Authorization, "
            "Content-Type"
        )

        response.headers[
            "Access-Control-Max-Age"
        ] = "600"

    def _cors_headers(
        self,
        origin: str,
        request: Request,
    ) -> list[
        tuple[bytes, bytes]
    ]:
        return [
            (
                b"access-control-allow-origin",
                origin.encode(
                    "latin-1"
                ),
            ),
            (
                b"vary",
                b"Origin",
            ),
            (
                b"access-control-allow-methods",
                b"GET, POST, OPTIONS",
            ),
            (
                b"access-control-allow-headers",
                (
                    b"Authorization, "
                    b"Content-Type"
                ),
            ),
        ]