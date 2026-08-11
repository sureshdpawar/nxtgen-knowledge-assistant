from uuid import UUID

from sqlalchemy.orm import Session

from app.models.tenant_llm_configuration import (
    TenantLLMConfiguration,
)
from app.repositories.tenant_llm_configuration_repository import (
    TenantLLMConfigurationRepository,
)
from app.schemas.tenant_llm_configuration import (
    UpdateTenantLLMConfigurationRequest,
)


class TenantLLMConfigurationService:

    def __init__(self):
        self.repository = (
            TenantLLMConfigurationRepository()
        )

    def get_active_configuration(
        self,
        db: Session,
        tenant_id: UUID,
    ) -> TenantLLMConfiguration | None:

        return self.repository.get_active_by_tenant_id(
            db=db,
            tenant_id=tenant_id,
        )

    def update_configuration(
        self,
        db: Session,
        tenant_id: UUID,
        payload: UpdateTenantLLMConfigurationRequest,
    ) -> TenantLLMConfiguration:

        configuration = (
            self.repository.get_active_by_tenant_id(
                db=db,
                tenant_id=tenant_id,
            )
        )

        if configuration is None:

            configuration = TenantLLMConfiguration(
                tenant_id=tenant_id,
            )

            db.add(configuration)

        configuration.provider = payload.provider
        configuration.model_name = payload.model_name
        configuration.base_url = payload.base_url
        configuration.api_key = payload.api_key
        configuration.temperature = (
            payload.temperature
        )
        configuration.max_tokens = (
            payload.max_tokens
        )
        configuration.is_active = (
            payload.is_active
        )

        db.commit()
        db.refresh(configuration)

        return configuration