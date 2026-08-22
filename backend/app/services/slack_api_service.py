import logging

import httpx


logger = logging.getLogger(
    "nxtgen.slack"
)


class SlackApiService:

    BASE_URL = (
        "https://slack.com/api"
    )

    def post_message(
        self,
        bot_token: str,
        channel_id: str,
        text: str,
        thread_ts:
            str | None = None,
    ) -> None:
        payload = {
            "channel":
                channel_id,

            "text":
                text,

            "unfurl_links":
                False,

            "unfurl_media":
                False,
        }

        if thread_ts:
            payload[
                "thread_ts"
            ] = thread_ts

        try:
            response = httpx.post(
                (
                    f"{self.BASE_URL}"
                    "/chat.postMessage"
                ),
                headers={
                    "Authorization":
                        (
                            "Bearer "
                            f"{bot_token}"
                        ),
                    "Content-Type":
                        "application/json",
                },
                json=payload,
                timeout=30.0,
            )

            response.raise_for_status()

        except httpx.HTTPError:
            logger.exception(
                "Slack HTTP request "
                "failed "
                "channel_id=%s",
                channel_id,
            )

            raise

        result = (
            response.json()
        )

        if not result.get(
            "ok"
        ):
            slack_error = (
                result.get(
                    "error"
                )
                or "unknown_error"
            )

            logger.error(
                "Slack API rejected "
                "chat.postMessage "
                "channel_id=%s "
                "error=%s",
                channel_id,
                slack_error,
            )

            raise RuntimeError(
                "Slack chat.postMessage "
                "failed: "
                f"{slack_error}"
            )