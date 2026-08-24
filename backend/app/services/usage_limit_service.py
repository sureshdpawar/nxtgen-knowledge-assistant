from uuid import UUID
from zoneinfo import (
    ZoneInfo,
    ZoneInfoNotFoundError,
)

from sqlalchemy.orm import Session

from app.models.chat_channel import (
    ChatChannel,
)
from app.models.knowledge_base import (
    KnowledgeBase,
)
from app.models.tenant import (
    Tenant,
)
from app.models.usage_limit import (
    UsageLimit,
)
from app.repositories.usage_limit_repository import (
    UsageLimitRepository,
)
from app.schemas.usage_limit import (
    UsageLimitCreate,
    UsageLimitUpdate,
)


class UsageLimitService:

    def __init__(self):
        self.repository = (
            UsageLimitRepository()
        )

    def create(
        self,
        db: Session,
        payload: UsageLimitCreate,
    ) -> UsageLimit:
        self._validate_timezone(
            payload.timezone
        )

        self._validate_scope(
            db=db,
            tenant_id=
                payload.tenant_id,
            knowledge_base_id=
                payload
                .knowledge_base_id,
            chat_channel_id=
                payload
                .chat_channel_id,
        )

        existing = (
            self._get_existing_scope_limit(
                db=db,
                tenant_id=
                    payload.tenant_id,
                knowledge_base_id=
                    payload
                    .knowledge_base_id,
                chat_channel_id=
                    payload
                    .chat_channel_id,
            )
        )

        if existing is not None:
            raise ValueError(
                "Usage limit already exists "
                "for this scope."
            )

        usage_limit = UsageLimit(
            tenant_id=
                payload.tenant_id,
            knowledge_base_id=
                payload
                .knowledge_base_id,
            chat_channel_id=
                payload
                .chat_channel_id,

            daily_message_limit=
                payload
                .daily_message_limit,

            daily_input_token_limit=
                payload
                .daily_input_token_limit,

            daily_output_token_limit=
                payload
                .daily_output_token_limit,

            daily_total_token_limit=
                payload
                .daily_total_token_limit,

            monthly_message_limit=
                payload
                .monthly_message_limit,

            monthly_input_token_limit=
                payload
                .monthly_input_token_limit,

            monthly_output_token_limit=
                payload
                .monthly_output_token_limit,

            monthly_total_token_limit=
                payload
                .monthly_total_token_limit,

            max_input_tokens_per_request=
                payload
                .max_input_tokens_per_request,

            max_output_tokens_per_request=
                payload
                .max_output_tokens_per_request,

            timezone=
                payload.timezone,

            enabled=
                payload.enabled,
        )

        usage_limit = (
            self.repository.create(
                db=db,
                entity=usage_limit,
            )
        )

        db.commit()

        db.refresh(
            usage_limit
        )

        return usage_limit

    def update(
        self,
        db: Session,
        usage_limit_id: UUID,
        payload: UsageLimitUpdate,
    ) -> UsageLimit:
        usage_limit = (
            self.repository.get(
                db=db,
                entity_id=
                    usage_limit_id,
            )
        )

        if usage_limit is None:
            raise ValueError(
                "Usage limit not found."
            )

        #
        # model_fields_set lets us
        # distinguish:
        #
        # omitted field
        #
        # from
        #
        # explicitly supplied null.
        #
        # That is important because
        # null means "remove this limit".
        #
        fields = (
            payload.model_fields_set
        )

        if (
            "timezone"
            in fields
            and payload.timezone
            is not None
        ):
            self._validate_timezone(
                payload.timezone
            )

        update_data = (
            payload.model_dump(
                exclude_unset=True,
            )
        )

        for (
            field_name,
            value,
        ) in update_data.items():
            setattr(
                usage_limit,
                field_name,
                value,
            )

        usage_limit = (
            self.repository.update(
                db=db,
                entity=usage_limit,
            )
        )

        db.commit()

        db.refresh(
            usage_limit
        )

        return usage_limit

    def get(
        self,
        db: Session,
        usage_limit_id: UUID,
    ) -> UsageLimit | None:
        return (
            self.repository.get(
                db=db,
                entity_id=
                    usage_limit_id,
            )
        )

    def get_tenant_limit(
        self,
        db: Session,
        tenant_id: UUID,
    ) -> UsageLimit | None:
        return (
            self.repository
            .get_tenant_limit(
                db=db,
                tenant_id=
                    tenant_id,
            )
        )

    def get_knowledge_base_limit(
        self,
        db: Session,
        knowledge_base_id: UUID,
    ) -> UsageLimit | None:
        return (
            self.repository
            .get_knowledge_base_limit(
                db=db,
                knowledge_base_id=
                    knowledge_base_id,
            )
        )

    def get_chat_channel_limit(
        self,
        db: Session,
        chat_channel_id: UUID,
    ) -> UsageLimit | None:
        return (
            self.repository
            .get_chat_channel_limit(
                db=db,
                chat_channel_id=
                    chat_channel_id,
            )
        )

    def delete(
        self,
        db: Session,
        usage_limit_id: UUID,
    ) -> None:
        usage_limit = (
            self.repository.get(
                db=db,
                entity_id=
                    usage_limit_id,
            )
        )

        if usage_limit is None:
            raise ValueError(
                "Usage limit not found."
            )

        self.repository.delete(
            db=db,
            entity=usage_limit,
        )

        db.commit()

    def _validate_scope(
        self,
        db: Session,
        tenant_id: UUID,
        knowledge_base_id: (
            UUID | None
        ),
        chat_channel_id: (
            UUID | None
        ),
    ) -> None:
        tenant = db.get(
            Tenant,
            tenant_id,
        )

        if tenant is None:
            raise ValueError(
                "Tenant not found."
            )

        knowledge_base = None

        if (
            knowledge_base_id
            is not None
        ):
            knowledge_base = db.get(
                KnowledgeBase,
                knowledge_base_id,
            )

            if knowledge_base is None:
                raise ValueError(
                    "Knowledge Base "
                    "not found."
                )

            if (
                knowledge_base.tenant_id
                != tenant_id
            ):
                raise ValueError(
                    "Knowledge Base does "
                    "not belong to the "
                    "supplied tenant."
                )

        if (
            chat_channel_id
            is not None
        ):
            if knowledge_base is None:
                raise ValueError(
                    "Channel-level usage "
                    "limits require a "
                    "Knowledge Base."
                )

            chat_channel = db.get(
                ChatChannel,
                chat_channel_id,
            )

            if chat_channel is None:
                raise ValueError(
                    "Chat channel "
                    "not found."
                )

            if (
                chat_channel.tenant_id
                != tenant_id
            ):
                raise ValueError(
                    "Chat channel does "
                    "not belong to the "
                    "supplied tenant."
                )

            if (
                chat_channel
                .knowledge_base_id
                != knowledge_base_id
            ):
                raise ValueError(
                    "Chat channel does "
                    "not belong to the "
                    "supplied Knowledge "
                    "Base."
                )

    def _get_existing_scope_limit(
        self,
        db: Session,
        tenant_id: UUID,
        knowledge_base_id: (
            UUID | None
        ),
        chat_channel_id: (
            UUID | None
        ),
    ) -> UsageLimit | None:
        if (
            chat_channel_id
            is not None
        ):
            return (
                self.repository
                .get_chat_channel_limit(
                    db=db,
                    chat_channel_id=
                        chat_channel_id,
                )
            )

        if (
            knowledge_base_id
            is not None
        ):
            return (
                self.repository
                .get_knowledge_base_limit(
                    db=db,
                    knowledge_base_id=
                        knowledge_base_id,
                )
            )

        return (
            self.repository
            .get_tenant_limit(
                db=db,
                tenant_id=
                    tenant_id,
            )
        )

    def _validate_timezone(
        self,
        timezone_name: str,
    ) -> None:
        try:
            ZoneInfo(
                timezone_name
            )

        except ZoneInfoNotFoundError as exc:
            raise ValueError(
                "Invalid timezone."
            ) from exc