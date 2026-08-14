from uuid import UUID

from sqlalchemy import (
    select,
    update,
)
from sqlalchemy.orm import Session

from app.models.tenant_llm_configuration import (
    TenantLLMConfiguration,
)
from app.repositories.base_repository import (
    BaseRepository,
)


class TenantLLMConfigurationRepository(
    BaseRepository[
        TenantLLMConfiguration
    ],
):

    def __init__(self):
        super().__init__(
            TenantLLMConfiguration,
        )

    def list_by_tenant(
        self,
        db: Session,
        tenant_id: UUID,
    ) -> list[
        TenantLLMConfiguration
    ]:

        stmt = (
            select(
                TenantLLMConfiguration,
            )
            .where(
                TenantLLMConfiguration
                .tenant_id
                == tenant_id,
            )
            .order_by(
                TenantLLMConfiguration
                .is_default
                .desc(),

                TenantLLMConfiguration
                .name,
            )
        )

        return list(
            db.scalars(
                stmt,
            ).all()
        )

    def get_by_id_and_tenant(
        self,
        db: Session,
        tenant_id: UUID,
        configuration_id: UUID,
    ) -> (
        TenantLLMConfiguration
        | None
    ):

        stmt = (
            select(
                TenantLLMConfiguration,
            )
            .where(
                TenantLLMConfiguration.id
                == configuration_id,

                TenantLLMConfiguration
                .tenant_id
                == tenant_id,
            )
        )

        return db.scalar(
            stmt,
        )

    def get_default_by_tenant_id(
        self,
        db: Session,
        tenant_id: UUID,
    ) -> (
        TenantLLMConfiguration
        | None
    ):

        stmt = (
            select(
                TenantLLMConfiguration,
            )
            .where(
                TenantLLMConfiguration
                .tenant_id
                == tenant_id,

                TenantLLMConfiguration
                .is_default
                .is_(True),

                TenantLLMConfiguration
                .is_active
                .is_(True),
            )
        )

        return db.scalar(
            stmt,
        )

    def clear_default(
        self,
        db: Session,
        tenant_id: UUID,
    ) -> None:

        stmt = (
            update(
                TenantLLMConfiguration,
            )
            .where(
                TenantLLMConfiguration
                .tenant_id
                == tenant_id,

                TenantLLMConfiguration
                .is_default
                .is_(True),
            )
            .values(
                is_default=False,
            )
        )

        db.execute(
            stmt,
        )

    # Temporary compatibility method.
    def get_active_by_tenant_id(
        self,
        db: Session,
        tenant_id: UUID,
    ) -> (
        TenantLLMConfiguration
        | None
    ):

        return (
            self.get_default_by_tenant_id(
                db=db,
                tenant_id=tenant_id,
            )
        )