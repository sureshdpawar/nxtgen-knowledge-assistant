from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Select,
    select,
)
from sqlalchemy.orm import Session

from app.models.online_eval_result import (
    OnlineEvalResult,
)
from app.repositories.base_repository import (
    BaseRepository,
)


class OnlineEvalResultRepository(
    BaseRepository[
        OnlineEvalResult
    ],
):

    def __init__(self):
        super().__init__(
            OnlineEvalResult,
        )

    def _apply_filters(
        self,
        stmt: Select,
        *,
        tenant_id: UUID,
        knowledge_base_id: (
            UUID | None
        ) = None,
        status: str | None = None,
        generator_provider: (
            str | None
        ) = None,
        generator_model: (
            str | None
        ) = None,
        passed: bool | None = None,
        source_trace_id: (
            str | None
        ) = None,
        created_from: (
            datetime | None
        ) = None,
        created_to: (
            datetime | None
        ) = None,
    ) -> Select:
        stmt = stmt.where(
            OnlineEvalResult.tenant_id
            == tenant_id
        )

        if knowledge_base_id is not None:
            stmt = stmt.where(
                OnlineEvalResult
                .knowledge_base_id
                == knowledge_base_id
            )

        if status is not None:
            stmt = stmt.where(
                OnlineEvalResult.status
                == status
            )

        if generator_provider is not None:
            stmt = stmt.where(
                OnlineEvalResult
                .generator_provider
                == generator_provider
            )

        if generator_model is not None:
            stmt = stmt.where(
                OnlineEvalResult
                .generator_model
                == generator_model
            )

        if passed is not None:
            stmt = stmt.where(
                OnlineEvalResult.passed
                == passed
            )

        if source_trace_id is not None:
            stmt = stmt.where(
                OnlineEvalResult
                .source_trace_id
                == source_trace_id
            )

        if created_from is not None:
            stmt = stmt.where(
                OnlineEvalResult.created_at
                >= created_from
            )

        if created_to is not None:
            stmt = stmt.where(
                OnlineEvalResult.created_at
                <= created_to
            )

        return stmt

    def list_pending(
        self,
        db: Session,
        *,
        tenant_id: UUID,
        limit: int = 100,
    ) -> list[
        OnlineEvalResult
    ]:
        if limit < 1:
            raise ValueError(
                "limit must be greater than 0."
            )

        stmt = (
            select(
                OnlineEvalResult
            )
            .where(
                OnlineEvalResult.tenant_id
                == tenant_id,

                OnlineEvalResult.status
                == "pending",
            )
            .order_by(
                OnlineEvalResult
                .created_at
                .asc()
            )
            .limit(
                limit
            )
        )

        return (
            db.execute(
                stmt
            )
            .scalars()
            .all()
        )

    def list_filtered(
        self,
        db: Session,
        *,
        tenant_id: UUID,
        knowledge_base_id: (
            UUID | None
        ) = None,
        status: str | None = None,
        generator_provider: (
            str | None
        ) = None,
        generator_model: (
            str | None
        ) = None,
        passed: bool | None = None,
        source_trace_id: (
            str | None
        ) = None,
        created_from: (
            datetime | None
        ) = None,
        created_to: (
            datetime | None
        ) = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[
        OnlineEvalResult
    ]:
        if limit < 1:
            raise ValueError(
                "limit must be greater than 0."
            )

        if offset < 0:
            raise ValueError(
                "offset cannot be negative."
            )

        stmt = select(
            OnlineEvalResult
        )

        stmt = self._apply_filters(
            stmt,
            tenant_id=
                tenant_id,
            knowledge_base_id=
                knowledge_base_id,
            status=
                status,
            generator_provider=
                generator_provider,
            generator_model=
                generator_model,
            passed=
                passed,
            source_trace_id=
                source_trace_id,
            created_from=
                created_from,
            created_to=
                created_to,
        )

        stmt = (
            stmt
            .order_by(
                OnlineEvalResult
                .created_at
                .desc()
            )
            .offset(
                offset
            )
            .limit(
                limit
            )
        )

        return (
            db.execute(
                stmt
            )
            .scalars()
            .all()
        )

    def get_for_tenant(
        self,
        db: Session,
        *,
        tenant_id: UUID,
        result_id: UUID,
    ) -> OnlineEvalResult | None:
        stmt = (
            select(
                OnlineEvalResult
            )
            .where(
                OnlineEvalResult.tenant_id
                == tenant_id,

                OnlineEvalResult.id
                == result_id,
            )
        )

        return (
            db.execute(
                stmt
            )
            .scalars()
            .first()
        )

    def list_by_trace_id(
        self,
        db: Session,
        *,
        tenant_id: UUID,
        source_trace_id: str,
    ) -> list[
        OnlineEvalResult
    ]:
        stmt = (
            select(
                OnlineEvalResult
            )
            .where(
                OnlineEvalResult.tenant_id
                == tenant_id,

                OnlineEvalResult
                .source_trace_id
                == source_trace_id,
            )
            .order_by(
                OnlineEvalResult
                .created_at
                .desc()
            )
        )

        return (
            db.execute(
                stmt
            )
            .scalars()
            .all()
        )

    def list_by_tenant(
        self,
        db: Session,
        *,
        tenant_id: UUID,
        limit: int = 100,
    ) -> list[
        OnlineEvalResult
    ]:
        return self.list_filtered(
            db=db,
            tenant_id=
                tenant_id,
            limit=
                limit,
        )

    def get_pending(
        self,
        db: Session,
        *,
        result_id: UUID,
    ) -> OnlineEvalResult | None:
        stmt = (
            select(
                OnlineEvalResult
            )
            .where(
                OnlineEvalResult.id
                == result_id,

                OnlineEvalResult.status
                == "pending",
            )
        )

        return (
            db.execute(
                stmt
            )
            .scalars()
            .first()
        )


    def list_for_summary(
        self,
        db: Session,
        *,
        tenant_id: UUID,
        knowledge_base_id: (
            UUID | None
        ) = None,
        generator_provider: (
            str | None
        ) = None,
        generator_model: (
            str | None
        ) = None,
        created_from: (
            datetime | None
        ) = None,
        created_to: (
            datetime | None
        ) = None,
    ) -> list[
        OnlineEvalResult
    ]:
        """
        Return tenant-scoped online evaluation rows
        used for summary aggregation.

        Aggregation stays in the service layer for v1
        because judge-cost data currently lives inside
        evaluation_metadata JSON.
        """

        stmt = select(
            OnlineEvalResult
        )

        stmt = self._apply_filters(
            stmt,
            tenant_id=
                tenant_id,
            knowledge_base_id=
                knowledge_base_id,
            generator_provider=
                generator_provider,
            generator_model=
                generator_model,
            created_from=
                created_from,
            created_to=
                created_to,
        )

        stmt = stmt.order_by(
            OnlineEvalResult
            .created_at
            .desc()
        )

        return (
            db.execute(
                stmt
            )
            .scalars()
            .all()
        )
