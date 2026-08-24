from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.orm import Session

from app.models.llm_usage_event import (
    LLMUsageEvent,
)
from app.repositories.base_repository import (
    BaseRepository,
)


class LLMUsageEventRepository(
    BaseRepository[
        LLMUsageEvent
    ],
):

    def __init__(self):
        super().__init__(
            LLMUsageEvent,
        )

    def get_usage(
        self,
        db: Session,
        tenant_id: UUID,
        start_at: datetime,
        end_at: datetime,
        knowledge_base_id: (
            UUID | None
        ) = None,
        chat_channel_id: (
            UUID | None
        ) = None,
        request_type: (
            str | None
        ) = "chat",
    ) -> dict:
        stmt = (
            select(
                func.count(
                    LLMUsageEvent.id
                ),
                func.coalesce(
                    func.sum(
                        LLMUsageEvent
                        .input_tokens
                    ),
                    0,
                ),
                func.coalesce(
                    func.sum(
                        LLMUsageEvent
                        .output_tokens
                    ),
                    0,
                ),
                func.coalesce(
                    func.sum(
                        LLMUsageEvent
                        .total_tokens
                    ),
                    0,
                ),
            )
            .where(
                LLMUsageEvent.tenant_id
                == tenant_id,

                LLMUsageEvent.created_at
                >= start_at,

                LLMUsageEvent.created_at
                < end_at,
            )
        )

        if (
            knowledge_base_id
            is not None
        ):
            stmt = stmt.where(
                LLMUsageEvent
                .knowledge_base_id
                == knowledge_base_id
            )

        if (
            chat_channel_id
            is not None
        ):
            stmt = stmt.where(
                LLMUsageEvent
                .chat_channel_id
                == chat_channel_id
            )

        if request_type is not None:
            stmt = stmt.where(
                LLMUsageEvent
                .request_type
                == request_type
            )

        row = db.execute(
            stmt
        ).one()

        return {
            "request_count":
                int(
                    row[0]
                    or 0
                ),

            "input_tokens":
                int(
                    row[1]
                    or 0
                ),

            "output_tokens":
                int(
                    row[2]
                    or 0
                ),

            "total_tokens":
                int(
                    row[3]
                    or 0
                ),
        }