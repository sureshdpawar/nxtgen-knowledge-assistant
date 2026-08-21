import base64
import hashlib
import hmac
import json
import secrets
import time

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import (
    ChatChannelStatus,
    ChatChannelType,
)
from app.models.chat_channel import (
    ChatChannel,
)


class WebsiteChannelSessionService:

    def get_channel(
        self,
        db: Session,
        channel_id: UUID,
    ) -> ChatChannel:
        channel = db.get(
            ChatChannel,
            channel_id,
        )

        if channel is None:
            raise ValueError(
                "Website channel not found."
            )

        if (
            channel.type
            != ChatChannelType.WEBSITE
        ):
            raise ValueError(
                "Channel is not a "
                "WEBSITE channel."
            )

        if (
            channel.status
            != ChatChannelStatus.ACTIVE
        ):
            raise ValueError(
                "Website channel is inactive."
            )

        return channel

    def normalize_origin(
        self,
        origin: str,
    ) -> str:
        return (
            origin
            .strip()
            .rstrip("/")
            .lower()
        )

    def validate_origin(
        self,
        channel: ChatChannel,
        origin: str | None,
    ) -> str:
        if not origin:
            raise ValueError(
                "Origin header is required."
            )

        normalized_origin = (
            self.normalize_origin(
                origin
            )
        )

        configuration = (
            channel.configuration
            or {}
        )

        allowed_origins = (
            configuration.get(
                "allowed_origins",
                [],
            )
            or []
        )

        normalized_allowed = {
            self.normalize_origin(
                str(value)
            )
            for value
            in allowed_origins
            if str(value).strip()
        }

        if (
            normalized_origin
            not in normalized_allowed
        ):
            raise ValueError(
                "Origin is not allowed "
                "for this website channel."
            )

        return normalized_origin

    def create_token(
        self,
        channel: ChatChannel,
        origin: str,
    ) -> tuple[
        str,
        int,
        str,
    ]:
        normalized_origin = (
            self.normalize_origin(
                origin
            )
        )

        ttl_seconds = (
            settings
            .WEBSITE_WIDGET_TOKEN_TTL_MINUTES
            * 60
        )

        now = int(
            time.time()
        )

        visitor_id = (
            secrets.token_urlsafe(
                18
            )
        )

        payload = {
            "tenant_id":
                str(
                    channel.tenant_id
                ),

            "channel_id":
                str(
                    channel.id
                ),

            "origin":
                normalized_origin,

            "visitor_id":
                visitor_id,

            "iat":
                now,

            "exp":
                now
                + ttl_seconds,
        }

        encoded_payload = (
            self._encode_payload(
                payload
            )
        )

        signature = (
            self._sign(
                encoded_payload
            )
        )

        token = (
            f"{encoded_payload}."
            f"{signature}"
        )

        return (
            token,
            ttl_seconds,
            visitor_id,
        )

    def verify_token(
        self,
        db: Session,
        token: str,
        origin: str | None,
    ) -> tuple[
        ChatChannel,
        str,
    ]:
        if not origin:
            raise ValueError(
                "Origin header is required."
            )

        try:
            (
                encoded_payload,
                signature,
            ) = token.split(
                ".",
                1,
            )

        except ValueError as exc:
            raise ValueError(
                "Invalid widget token."
            ) from exc

        expected_signature = (
            self._sign(
                encoded_payload
            )
        )

        if not hmac.compare_digest(
            signature,
            expected_signature,
        ):
            raise ValueError(
                "Invalid widget token."
            )

        payload = (
            self._decode_payload(
                encoded_payload
            )
        )

        expires_at = (
            payload.get(
                "exp"
            )
        )

        if (
            not isinstance(
                expires_at,
                int,
            )
            or expires_at
            <= int(
                time.time()
            )
        ):
            raise ValueError(
                "Widget token has expired."
            )

        issued_at = (
            payload.get(
                "iat"
            )
        )

        if not isinstance(
            issued_at,
            int,
        ):
            raise ValueError(
                "Invalid widget token."
            )

        if (
            issued_at
            > int(time.time()) + 60
        ):
            raise ValueError(
                "Invalid widget token."
            )

        normalized_origin = (
            self.normalize_origin(
                origin
            )
        )

        token_origin = (
            self.normalize_origin(
                str(
                    payload.get(
                        "origin",
                        "",
                    )
                )
            )
        )

        if (
            token_origin
            != normalized_origin
        ):
            raise ValueError(
                "Widget token origin "
                "does not match request."
            )

        try:
            channel_id = UUID(
                str(
                    payload[
                        "channel_id"
                    ]
                )
            )

        except (
            KeyError,
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "Invalid widget token."
            ) from exc

        channel = self.get_channel(
            db=db,
            channel_id=channel_id,
        )

        #
        # Re-check current channel
        # configuration on every request.
        #
        self.validate_origin(
            channel=channel,
            origin=origin,
        )

        token_tenant_id = str(
            payload.get(
                "tenant_id",
                "",
            )
        )

        if (
            token_tenant_id
            != str(
                channel.tenant_id
            )
        ):
            raise ValueError(
                "Invalid widget token."
            )

        visitor_id = str(
            payload.get(
                "visitor_id",
                "",
            )
        ).strip()

        if not visitor_id:
            raise ValueError(
                "Invalid widget token."
            )

        return (
            channel,
            visitor_id,
        )

    def _sign(
        self,
        value: str,
    ) -> str:
        secret = (
            settings
            .WEBSITE_WIDGET_TOKEN_SECRET
            .encode(
                "utf-8"
            )
        )

        digest = hmac.new(
            secret,
            value.encode(
                "utf-8"
            ),
            hashlib.sha256,
        ).digest()

        return (
            base64
            .urlsafe_b64encode(
                digest
            )
            .decode(
                "utf-8"
            )
            .rstrip("=")
        )

    def _encode_payload(
        self,
        payload: dict,
    ) -> str:
        raw = json.dumps(
            payload,
            separators=(
                ",",
                ":",
            ),
            sort_keys=True,
        ).encode(
            "utf-8"
        )

        return (
            base64
            .urlsafe_b64encode(
                raw
            )
            .decode(
                "utf-8"
            )
            .rstrip("=")
        )

    def _decode_payload(
        self,
        encoded_payload: str,
    ) -> dict:
        padding = (
            "="
            * (
                -len(
                    encoded_payload
                )
                % 4
            )
        )

        try:
            raw = (
                base64
                .urlsafe_b64decode(
                    encoded_payload
                    + padding
                )
            )

            payload = json.loads(
                raw.decode(
                    "utf-8"
                )
            )

        except Exception as exc:
            raise ValueError(
                "Invalid widget token."
            ) from exc

        if not isinstance(
            payload,
            dict,
        ):
            raise ValueError(
                "Invalid widget token."
            )

        return payload