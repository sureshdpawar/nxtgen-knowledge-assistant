from dataclasses import dataclass
from datetime import (
    UTC,
    datetime,
    timedelta,
)
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.core.config import settings
from app.exceptions.usage import (
    UsageQuotaExceededError,
)
from app.models.usage_limit import (
    UsageLimit,
)
from app.repositories.llm_usage_event_repository import (
    LLMUsageEventRepository,
)
from app.repositories.usage_limit_repository import (
    UsageLimitRepository,
)


@dataclass
class EffectiveUsageLimit:
    daily_message_limit: int | None

    daily_input_token_limit: int | None

    daily_output_token_limit: int | None

    daily_total_token_limit: int | None

    monthly_message_limit: int | None

    monthly_input_token_limit: int | None

    monthly_output_token_limit: int | None

    monthly_total_token_limit: int | None

    max_input_tokens_per_request: int | None

    max_output_tokens_per_request: int | None

    timezone: str

    enabled: bool


class UsageQuotaService:

    def __init__(self):
        self.limit_repository = (
            UsageLimitRepository()
        )

        self.usage_repository = (
            LLMUsageEventRepository()
        )

    def check_chat_allowed(
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
        estimated_input_tokens: int = 0,
        reserved_output_tokens: int = 0,
    ) -> dict:
        if estimated_input_tokens < 0:
            raise ValueError(
                "estimated_input_tokens "
                "cannot be negative."
            )

        if reserved_output_tokens < 0:
            raise ValueError(
                "reserved_output_tokens "
                "cannot be negative."
            )

        limits = (
            self.get_effective_limits(
                db=db,
                tenant_id=
                    tenant_id,
                knowledge_base_id=
                    knowledge_base_id,
                chat_channel_id=
                    chat_channel_id,
            )
        )

        checks = []

        for (
            scope,
            source,
            usage_limit,
        ) in limits:
            result = (
                self._check_scope(
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
                    estimated_input_tokens=
                        estimated_input_tokens,
                    reserved_output_tokens=
                        reserved_output_tokens,
                )
            )

            checks.append(
                result
            )

        return {
            "allowed":
                True,

            "checks":
                checks,
        }

    def get_effective_limits(
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
    ) -> list[
        tuple[
            str,
            str,
            EffectiveUsageLimit,
        ]
    ]:
        limits = []

        #
        # Start with platform defaults.
        #
        platform_limit = (
            self._platform_default_limit()
        )

        tenant_row = (
            self.limit_repository
            .get_tenant_limit(
                db=db,
                tenant_id=
                    tenant_id,
            )
        )

        #
        # Merge tenant overrides on top
        # of platform defaults.
        #
        tenant_effective = (
            self._merge_limit(
                parent=
                    platform_limit,
                override=
                    tenant_row,
            )
        )

        tenant_source = (
            "tenant_override"
            if tenant_row is not None
            else "platform_default"
        )

        limits.append(
            (
                "tenant",
                tenant_source,
                tenant_effective,
            )
        )

        parent_effective = (
            tenant_effective
        )

        #
        # KB scope only exists when there
        # is an explicit KB override row.
        #
        if (
            knowledge_base_id
            is not None
        ):
            kb_row = (
                self.limit_repository
                .get_knowledge_base_limit(
                    db=db,
                    knowledge_base_id=
                        knowledge_base_id,
                )
            )

            if kb_row is not None:
                kb_effective = (
                    self._merge_limit(
                        parent=
                            tenant_effective,
                        override=
                            kb_row,
                    )
                )

                limits.append(
                    (
                        "knowledge_base",
                        "knowledge_base_override",
                        kb_effective,
                    )
                )

                parent_effective = (
                    kb_effective
                )

        #
        # Channel scope only exists when
        # there is an explicit channel row.
        #
        if (
            chat_channel_id
            is not None
        ):
            channel_row = (
                self.limit_repository
                .get_chat_channel_limit(
                    db=db,
                    chat_channel_id=
                        chat_channel_id,
                )
            )

            if channel_row is not None:
                channel_effective = (
                    self._merge_limit(
                        parent=
                            parent_effective,
                        override=
                            channel_row,
                    )
                )

                limits.append(
                    (
                        "chat_channel",
                        "chat_channel_override",
                        channel_effective,
                    )
                )

        return limits

    def _platform_default_limit(
        self,
    ) -> EffectiveUsageLimit:
        return EffectiveUsageLimit(
            daily_message_limit=
                settings
                .DEFAULT_DAILY_MESSAGE_LIMIT,

            daily_input_token_limit=
                settings
                .DEFAULT_DAILY_INPUT_TOKEN_LIMIT,

            daily_output_token_limit=
                settings
                .DEFAULT_DAILY_OUTPUT_TOKEN_LIMIT,

            daily_total_token_limit=
                settings
                .DEFAULT_DAILY_TOTAL_TOKEN_LIMIT,

            monthly_message_limit=
                settings
                .DEFAULT_MONTHLY_MESSAGE_LIMIT,

            monthly_input_token_limit=
                settings
                .DEFAULT_MONTHLY_INPUT_TOKEN_LIMIT,

            monthly_output_token_limit=
                settings
                .DEFAULT_MONTHLY_OUTPUT_TOKEN_LIMIT,

            monthly_total_token_limit=
                settings
                .DEFAULT_MONTHLY_TOTAL_TOKEN_LIMIT,

            max_input_tokens_per_request=
                settings
                .DEFAULT_MAX_INPUT_TOKENS_PER_REQUEST,

            max_output_tokens_per_request=
                settings
                .DEFAULT_MAX_OUTPUT_TOKENS_PER_REQUEST,

            timezone=
                settings
                .DEFAULT_USAGE_TIMEZONE,

            enabled=True,
        )

    def _merge_limit(
        self,
        *,
        parent: EffectiveUsageLimit,
        override: UsageLimit | None,
    ) -> EffectiveUsageLimit:
        if override is None:
            return parent

        return EffectiveUsageLimit(
            daily_message_limit=
                self._inherit(
                    override
                    .daily_message_limit,
                    parent
                    .daily_message_limit,
                ),

            daily_input_token_limit=
                self._inherit(
                    override
                    .daily_input_token_limit,
                    parent
                    .daily_input_token_limit,
                ),

            daily_output_token_limit=
                self._inherit(
                    override
                    .daily_output_token_limit,
                    parent
                    .daily_output_token_limit,
                ),

            daily_total_token_limit=
                self._inherit(
                    override
                    .daily_total_token_limit,
                    parent
                    .daily_total_token_limit,
                ),

            monthly_message_limit=
                self._inherit(
                    override
                    .monthly_message_limit,
                    parent
                    .monthly_message_limit,
                ),

            monthly_input_token_limit=
                self._inherit(
                    override
                    .monthly_input_token_limit,
                    parent
                    .monthly_input_token_limit,
                ),

            monthly_output_token_limit=
                self._inherit(
                    override
                    .monthly_output_token_limit,
                    parent
                    .monthly_output_token_limit,
                ),

            monthly_total_token_limit=
                self._inherit(
                    override
                    .monthly_total_token_limit,
                    parent
                    .monthly_total_token_limit,
                ),

            max_input_tokens_per_request=
                self._inherit(
                    override
                    .max_input_tokens_per_request,
                    parent
                    .max_input_tokens_per_request,
                ),

            max_output_tokens_per_request=
                self._inherit(
                    override
                    .max_output_tokens_per_request,
                    parent
                    .max_output_tokens_per_request,
                ),

            #
            # Empty/NULL timezone is not allowed
            # by our schema, but keeping this
            # defensive makes inheritance clear.
            #
            timezone=(
                override.timezone
                or parent.timezone
            ),

            #
            # enabled is an explicit scope
            # kill switch, not an inherited
            # nullable value.
            #
            enabled=
                override.enabled,
        )

    def _inherit(
        self,
        override_value: int | None,
        parent_value: int | None,
    ) -> int | None:
        if override_value is None:
            return parent_value

        return override_value

    def _check_scope(
        self,
        db: Session,
        *,
        scope: str,
        source: str,
        usage_limit: EffectiveUsageLimit,
        tenant_id: UUID,
        knowledge_base_id: (
            UUID | None
        ),
        chat_channel_id: (
            UUID | None
        ),
        estimated_input_tokens: int,
        reserved_output_tokens: int,
    ) -> dict:
        if not usage_limit.enabled:
            raise (
                UsageQuotaExceededError(
                    (
                        "Chat is disabled "
                        "for this scope."
                    ),
                    scope=
                        scope,
                )
            )

        self._check_per_request_limits(
            scope=
                scope,
            usage_limit=
                usage_limit,
            estimated_input_tokens=
                estimated_input_tokens,
            reserved_output_tokens=
                reserved_output_tokens,
        )

        (
            daily_start,
            daily_end,
        ) = self._daily_window(
            usage_limit.timezone
        )

        (
            monthly_start,
            monthly_end,
        ) = self._monthly_window(
            usage_limit.timezone
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

        reservation = {
            "messages":
                1,

            "input_tokens":
                estimated_input_tokens,

            "output_tokens":
                reserved_output_tokens,

            "total_tokens":
                (
                    estimated_input_tokens
                    + reserved_output_tokens
                ),
        }

        self._check_period_limits(
            scope=
                scope,
            period=
                "daily",
            usage=
                daily_usage,
            usage_limit=
                usage_limit,
            reservation=
                reservation,
            reset_at=
                daily_end,
        )

        self._check_period_limits(
            scope=
                scope,
            period=
                "monthly",
            usage=
                monthly_usage,
            usage_limit=
                usage_limit,
            reservation=
                reservation,
            reset_at=
                monthly_end,
        )

        return {
            "scope":
                scope,

            "source":
                source,

            "timezone":
                usage_limit.timezone,

            "daily_usage":
                daily_usage,

            "monthly_usage":
                monthly_usage,

            "daily_reset_at":
                daily_end
                .isoformat(),

            "monthly_reset_at":
                monthly_end
                .isoformat(),
        }

    def _check_per_request_limits(
        self,
        *,
        scope: str,
        usage_limit: EffectiveUsageLimit,
        estimated_input_tokens: int,
        reserved_output_tokens: int,
    ) -> None:
        input_limit = (
            usage_limit
            .max_input_tokens_per_request
        )

        if (
            input_limit is not None
            and estimated_input_tokens
            > input_limit
        ):
            raise (
                UsageQuotaExceededError(
                    (
                        "Maximum input "
                        "tokens per request "
                        "exceeded."
                    ),
                    scope=
                        scope,
                    period=
                        "request",
                    metric=
                        "input_tokens",
                    limit=
                        input_limit,
                    used=
                        estimated_input_tokens,
                )
            )

        output_limit = (
            usage_limit
            .max_output_tokens_per_request
        )

        if (
            output_limit is not None
            and reserved_output_tokens
            > output_limit
        ):
            raise (
                UsageQuotaExceededError(
                    (
                        "Maximum output "
                        "tokens per request "
                        "exceeded."
                    ),
                    scope=
                        scope,
                    period=
                        "request",
                    metric=
                        "output_tokens",
                    limit=
                        output_limit,
                    used=
                        reserved_output_tokens,
                )
            )

    def _check_period_limits(
        self,
        *,
        scope: str,
        period: str,
        usage: dict,
        usage_limit: EffectiveUsageLimit,
        reservation: dict,
        reset_at: datetime,
    ) -> None:
        mappings = (
            (
                "messages",
                "request_count",
                (
                    usage_limit
                    .daily_message_limit
                    if period == "daily"
                    else usage_limit
                    .monthly_message_limit
                ),
            ),
            (
                "input_tokens",
                "input_tokens",
                (
                    usage_limit
                    .daily_input_token_limit
                    if period == "daily"
                    else usage_limit
                    .monthly_input_token_limit
                ),
            ),
            (
                "output_tokens",
                "output_tokens",
                (
                    usage_limit
                    .daily_output_token_limit
                    if period == "daily"
                    else usage_limit
                    .monthly_output_token_limit
                ),
            ),
            (
                "total_tokens",
                "total_tokens",
                (
                    usage_limit
                    .daily_total_token_limit
                    if period == "daily"
                    else usage_limit
                    .monthly_total_token_limit
                ),
            ),
        )

        for (
            metric,
            usage_key,
            limit,
        ) in mappings:
            if limit is None:
                continue

            used = int(
                usage[
                    usage_key
                ]
            )

            reserved = int(
                reservation[
                    metric
                ]
            )

            projected = (
                used
                + reserved
            )

            if projected > limit:
                raise (
                    UsageQuotaExceededError(
                        (
                            f"{period.capitalize()} "
                            f"{metric.replace('_', ' ')} "
                            "limit reached."
                        ),
                        scope=
                            scope,
                        period=
                            period,
                        metric=
                            metric,
                        limit=
                            limit,
                        used=
                            used,
                        reset_at=
                            reset_at
                            .isoformat(),
                    )
                )

    def _daily_window(
        self,
        timezone_name: str,
    ) -> tuple[
        datetime,
        datetime,
    ]:
        timezone = ZoneInfo(
            timezone_name
        )

        now_local = (
            datetime.now(
                UTC
            )
            .astimezone(
                timezone
            )
        )

        start_local = (
            now_local
            .replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
        )

        end_local = (
            start_local
            + timedelta(
                days=1
            )
        )

        return (
            start_local
            .astimezone(
                UTC
            ),
            end_local
            .astimezone(
                UTC
            ),
        )

    def _monthly_window(
        self,
        timezone_name: str,
    ) -> tuple[
        datetime,
        datetime,
    ]:
        timezone = ZoneInfo(
            timezone_name
        )

        now_local = (
            datetime.now(
                UTC
            )
            .astimezone(
                timezone
            )
        )

        start_local = (
            now_local
            .replace(
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
        )

        if start_local.month == 12:
            end_local = (
                start_local
                .replace(
                    year=
                        start_local.year
                        + 1,
                    month=1,
                )
            )

        else:
            end_local = (
                start_local
                .replace(
                    month=
                        start_local.month
                        + 1,
                )
            )

        return (
            start_local
            .astimezone(
                UTC
            ),
            end_local
            .astimezone(
                UTC
            ),
        )