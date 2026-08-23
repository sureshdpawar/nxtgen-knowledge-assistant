import hashlib
import hmac
import time


class SlackRequestVerificationService:

    SIGNATURE_VERSION = "v0"

    MAX_REQUEST_AGE_SECONDS = 60 * 5

    def verify(
        self,
        signing_secret: str,
        timestamp: str | None,
        signature: str | None,
        raw_body: bytes,
    ) -> bool:
        if not signing_secret:
            return False

        if not timestamp:
            return False

        if not signature:
            return False

        try:
            request_timestamp = int(
                timestamp
            )

        except (
            TypeError,
            ValueError,
        ):
            return False

        current_timestamp = int(
            time.time()
        )

        if (
            abs(
                current_timestamp
                - request_timestamp
            )
            > self.MAX_REQUEST_AGE_SECONDS
        ):
            return False

        try:
            body_text = raw_body.decode(
                "utf-8"
            )

        except UnicodeDecodeError:
            return False

        base_string = (
            f"{self.SIGNATURE_VERSION}:"
            f"{timestamp}:"
            f"{body_text}"
        )

        digest = hmac.new(
            signing_secret.encode(
                "utf-8"
            ),
            base_string.encode(
                "utf-8"
            ),
            hashlib.sha256,
        ).hexdigest()

        expected_signature = (
            f"{self.SIGNATURE_VERSION}="
            f"{digest}"
        )

        return hmac.compare_digest(
            expected_signature,
            signature,
        )