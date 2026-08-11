from uuid import UUID

from sqlalchemy.orm import Session

from app.models.tenant_llm_configuration import (
    TenantLLMConfiguration,
)
from app.repositories.base_repository import (
    BaseRepository,
)


class TenantLLMConfigurationRepository(
    BaseRepository[TenantLLMConfiguration],
):

    def __init__(self):
        super().__init__(
            TenantLLMConfiguration,
        )

    def get_active_by_tenant_id(
        self,
        db: Session,
        tenant_id: UUID,
    ) -> TenantLLMConfiguration | None:

        return (
            db.query(
                TenantLLMConfiguration,
            )
            .filter(
                TenantLLMConfiguration.tenant_id == tenant_id,
                TenantLLMConfiguration.is_active.is_(True),
            )
            .first()
        )