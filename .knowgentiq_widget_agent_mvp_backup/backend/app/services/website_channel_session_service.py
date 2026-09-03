import base64
import hashlib
import hmac
import json
import secrets
import time

from uuid import UUID, uuid4
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import ChatChannelStatus, ChatChannelType
from app.models.chat_channel import ChatChannel


class WebsiteChannelSessionService:
    def get_channel(self, db: Session, channel_id: UUID) -> ChatChannel:
        channel = db.get(ChatChannel, channel_id)

        if channel is None:
            raise ValueError("Website channel not found.")

        if channel.type != ChatChannelType.WEBSITE:
            raise ValueError("Channel is not a WEBSITE channel.")

        if channel.status != ChatChannelStatus.ACTIVE:
            raise ValueError("Website channel is inactive.")

        return channel

    def normalize_origin(self, origin: str) -> str:
        return origin.strip().rstrip("/").lower()

    def validate_origin(
        self,
        channel: ChatChannel,
        origin: str | None,
    ) -> str:
        if not origin:
            raise ValueError("Origin header is required.")

        normalized_origin = self.normalize_origin(origin)
        allowed_origins = (
            (channel.configuration or {}).get("allowed_origins", [])
            or []
        )

        normalized_allowed = {
            self.normalize_origin(str(value))
            for value in allowed_origins
            if str(value).strip()
        }

        if normalized_origin not in normalized_allowed:
            raise ValueError(
                "Origin is not allowed for this website channel."
            )

        return normalized_origin

    def create_token(
        self,
        channel: ChatChannel,
        origin: str,
        *,
        runtime_context: dict | None = None,
    ) -> tuple[str, int, str, UUID]:
        ttl_seconds = (
            settings.WEBSITE_WIDGET_TOKEN_TTL_MINUTES * 60
        )
        now = int(time.time())
        visitor_id = secrets.token_urlsafe(18)
        thread_id = uuid4()

        payload = {
            "tenant_id": str(channel.tenant_id),
            "channel_id": str(channel.id),
            "origin": self.normalize_origin(origin),
            "visitor_id": visitor_id,
            "thread_id": str(thread_id),
            "runtime_context": runtime_context or {},
            "iat": now,
            "exp": now + ttl_seconds,
        }

        encoded = self._encode_payload(payload)
        token = f"{encoded}.{self._sign(encoded)}"

        return token, ttl_seconds, visitor_id, thread_id

    def verify_token(
        self,
        db: Session,
        token: str,
        origin: str | None,
    ) -> tuple[ChatChannel, str, UUID, dict]:
        if not origin:
            raise ValueError("Origin header is required.")

        try:
            encoded, signature = token.split(".", 1)
        except ValueError as exc:
            raise ValueError("Invalid widget token.") from exc

        if not hmac.compare_digest(
            signature,
            self._sign(encoded),
        ):
            raise ValueError("Invalid widget token.")

        payload = self._decode_payload(encoded)

        if (
            not isinstance(payload.get("exp"), int)
            or payload["exp"] <= int(time.time())
        ):
            raise ValueError("Widget token has expired.")

        if (
            self.normalize_origin(str(payload.get("origin", "")))
            != self.normalize_origin(origin)
        ):
            raise ValueError(
                "Widget token origin does not match request."
            )

        try:
            channel_id = UUID(str(payload["channel_id"]))
            thread_id = UUID(str(payload["thread_id"]))
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Invalid widget token.") from exc

        channel = self.get_channel(
            db=db,
            channel_id=channel_id,
        )
        self.validate_origin(
            channel=channel,
            origin=origin,
        )

        if (
            str(payload.get("tenant_id", ""))
            != str(channel.tenant_id)
        ):
            raise ValueError("Invalid widget token.")

        visitor_id = str(payload.get("visitor_id", "")).strip()
        if not visitor_id:
            raise ValueError("Invalid widget token.")

        runtime_context = payload.get("runtime_context", {}) or {}
        if not isinstance(runtime_context, dict):
            raise ValueError("Invalid widget token.")

        return channel, visitor_id, thread_id, runtime_context

    def _sign(self, value: str) -> str:
        secret = (
            settings.WEBSITE_WIDGET_TOKEN_SECRET
            .encode("utf-8")
        )
        digest = hmac.new(
            secret,
            value.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        return (
            base64.urlsafe_b64encode(digest)
            .decode("utf-8")
            .rstrip("=")
        )

    def _encode_payload(self, payload: dict) -> str:
        raw = json.dumps(
            payload,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return (
            base64.urlsafe_b64encode(raw)
            .decode("utf-8")
            .rstrip("=")
        )

    def _decode_payload(self, encoded: str) -> dict:
        padding = "=" * (-len(encoded) % 4)

        try:
            raw = base64.urlsafe_b64decode(encoded + padding)
            payload = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise ValueError("Invalid widget token.") from exc

        if not isinstance(payload, dict):
            raise ValueError("Invalid widget token.")

        return payload
