from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.llm_usage_event_repository import (
    LLMUsageEventRepository,
)
from app.services.usage_quota_service import (
    EffectiveUsageLimit,
    UsageQuotaService,
)


class UsageStatusService:

    def __init__(
        self,
    ):
        self.usage_repository = (
            LLMUsageEventRepository()
        )

        self.quota_service = (
            UsageQuotaService()
        )

    def get_status(
        self,
        db: Session,
        *,
        tenant_id: UUID,
        knowledge_base_id: (
            UUID | None
        ) = None,
        chat_channel_id: (
            UUID | None
        ) = None,
    ) -> dict:
        scopes = []

        effective_limits = (
            self.quota_service
            .get_effective_limits(
                db=db,
                tenant_id=
                    tenant_id,
                knowledge_base_id=
                    knowledge_base_id,
                chat_channel_id=
                    chat_channel_id,
            )
        )

        for (
            scope,
            source,
            usage_limit,
        ) in effective_limits:
            scopes.append(
                self._build_scope_status(
                    db=db,
                    scope=
                        scope,
                    source=
                        source,
                    usage_limit=
                        usage_limit,
                    tenant_id=
                        tenant_id,
                    knowledge_base_id=
                        (
                            knowledge_base_id
                            if scope
                            in (
                                "knowledge_base",
                                "chat_channel",
                            )
                            else None
                        ),
                    chat_channel_id=
                        (
                            chat_channel_id
                            if scope
                            == "chat_channel"
                            else None
                        ),
                )
            )

        allowed = all(
            scope[
                "enabled"
            ]
            and self._period_allowed(
                scope[
                    "daily"
                ]
            )
            and self._period_allowed(
                scope[
                    "monthly"
                ]
            )
            for scope in scopes
        )

        return {
            "allowed":
                allowed,

            "scopes":
                scopes,
        }

    def _build_scope_status(
        self,
        db: Session,
        *,
        scope: str,
        source: str,
        usage_limit: EffectiveUsageLimit,
        tenant_id: UUID,
        knowledge_base_id: (
            UUID | None
        ) = None,
        chat_channel_id: (
            UUID | None
        ) = None,
    ) -> dict:
        (
            daily_start,
            daily_end,
        ) = (
            self.quota_service
            ._daily_window(
                usage_limit.timezone
            )
        )

        (
            monthly_start,
            monthly_end,
        ) = (
            self.quota_service
            ._monthly_window(
                usage_limit.timezone
            )
        )

        daily_usage = (
            self.usage_repository
            .get_usage(
                db=db,
                tenant_id=
                    tenant_id,
                knowledge_base_id=
                    knowledge_base_id,
                chat_channel_id=
                    chat_channel_id,
                start_at=
                    daily_start,
                end_at=
                    daily_end,
                request_type=
                    "chat",
            )
        )

        monthly_usage = (
            self.usage_repository
            .get_usage(
                db=db,
                tenant_id=
                    tenant_id,
                knowledge_base_id=
                    knowledge_base_id,
                chat_channel_id=
                    chat_channel_id,
                start_at=
                    monthly_start,
                end_at=
                    monthly_end,
                request_type=
                    "chat",
            )
        )

        return {
            "scope":
                scope,

            "source":
                source,

            "enabled":
                usage_limit.enabled,

            "timezone":
                usage_limit.timezone,

            "daily":
                self._build_period_status(
                    usage=
                        daily_usage,
                    message_limit=
                        usage_limit
                        .daily_message_limit,
                    input_token_limit=
                        usage_limit
                        .daily_input_token_limit,
                    output_token_limit=
                        usage_limit
                        .daily_output_token_limit,
                    total_token_limit=
                        usage_limit
                        .daily_total_token_limit,
                    reset_at=
                        daily_end
                        .isoformat(),
                ),

            "monthly":
                self._build_period_status(
                    usage=
                        monthly_usage,
                    message_limit=
                        usage_limit
                        .monthly_message_limit,
                    input_token_limit=
                        usage_limit
                        .monthly_input_token_limit,
                    output_token_limit=
                        usage_limit
                        .monthly_output_token_limit,
                    total_token_limit=
                        usage_limit
                        .monthly_total_token_limit,
                    reset_at=
                        monthly_end
                        .isoformat(),
                ),
        }

    def _build_period_status(
        self,
        *,
        usage: dict,
        message_limit: int | None,
        input_token_limit: int | None,
        output_token_limit: int | None,
        total_token_limit: int | None,
        reset_at: str,
    ) -> dict:
        return {
            "messages":
                self._metric(
                    used=
                        usage[
                            "request_count"
                        ],
                    limit=
                        message_limit,
                ),

            "input_tokens":
                self._metric(
                    used=
                        usage[
                            "input_tokens"
                        ],
                    limit=
                        input_token_limit,
                ),

            "output_tokens":
                self._metric(
                    used=
                        usage[
                            "output_tokens"
                        ],
                    limit=
                        output_token_limit,
                ),

            "total_tokens":
                self._metric(
                    used=
                        usage[
                            "total_tokens"
                        ],
                    limit=
                        total_token_limit,
                ),

            "reset_at":
                reset_at,
        }

    def _metric(
        self,
        *,
        used: int,
        limit: int | None,
    ) -> dict:
        if limit is None:
            return {
                "used":
                    used,

                "limit":
                    None,

                "remaining":
                    None,

                "percentage_used":
                    None,
            }

        remaining = max(
            limit - used,
            0,
        )

        percentage_used = (
            100.0
            if limit == 0
            else round(
                (
                    used
                    / limit
                )
                * 100,
                2,
            )
        )

        return {
            "used":
                used,

            "limit":
                limit,

            "remaining":
                remaining,

            "percentage_used":
                percentage_used,
        }

    def _period_allowed(
        self,
        period: dict,
    ) -> bool:
        for key in (
            "messages",
            "input_tokens",
            "output_tokens",
            "total_tokens",
        ):
            metric = (
                period[
                    key
                ]
            )

            limit = (
                metric[
                    "limit"
                ]
            )

            if limit is None:
                continue

            if (
                metric[
                    "used"
                ]
                >= limit
            ):
                return False

        return True