from uuid import UUID

from sqlalchemy.orm import Session

from app.models.knowledge_base import (
    KnowledgeBase,
)
from app.models.tenant_llm_configuration import (
    TenantLLMConfiguration,
)
from app.repositories.tenant_llm_configuration_repository import (
    TenantLLMConfigurationRepository,
)
from app.schemas.tenant_llm_configuration import (
    CreateTenantLLMConfigurationRequest,
    UpdateTenantLLMConfigurationRequest,
)


class TenantLLMConfigurationService:

    def __init__(self):
        self.repository = (
            TenantLLMConfigurationRepository()
        )

    def list_profiles(
        self,
        db: Session,
        tenant_id: UUID,
    ) -> list[
        TenantLLMConfiguration
    ]:

        return (
            self.repository.list_by_tenant(
                db=db,
                tenant_id=tenant_id,
            )
        )

    def get_profile(
        self,
        db: Session,
        tenant_id: UUID,
        configuration_id: UUID,
    ) -> TenantLLMConfiguration:

        configuration = (
            self.repository
            .get_by_id_and_tenant(
                db=db,
                tenant_id=tenant_id,
                configuration_id=
                    configuration_id,
            )
        )

        if configuration is None:
            raise ValueError(
                "LLM configuration "
                "not found."
            )

        return configuration

    def get_default_configuration(
        self,
        db: Session,
        tenant_id: UUID,
    ) -> (
        TenantLLMConfiguration
        | None
    ):

        return (
            self.repository
            .get_default_by_tenant_id(
                db=db,
                tenant_id=tenant_id,
            )
        )

    def create_profile(
        self,
        db: Session,
        tenant_id: UUID,
        payload:
            CreateTenantLLMConfigurationRequest,
    ) -> TenantLLMConfiguration:

        profiles = (
            self.repository.list_by_tenant(
                db=db,
                tenant_id=tenant_id,
            )
        )

        should_be_default = (
            payload.is_default
            or len(profiles) == 0
        )

        if should_be_default:
            self.repository.clear_default(
                db=db,
                tenant_id=tenant_id,
            )

        configuration = (
            TenantLLMConfiguration(
                tenant_id=
                    tenant_id,

                name=
                    payload.name,

                provider=
                    payload.provider,

                model_name=
                    payload.model_name,

                base_url=
                    payload.base_url,

                api_key=
                    payload.api_key,

                temperature=
                    payload.temperature,

                max_tokens=
                    payload.max_tokens,

                is_active=
                    payload.is_active,

                is_default=
                    should_be_default,
            )
        )

        db.add(
            configuration,
        )

        db.commit()
        db.refresh(
            configuration,
        )

        return configuration

    def update_profile(
        self,
        db: Session,
        tenant_id: UUID,
        configuration_id: UUID,
        payload:
            UpdateTenantLLMConfigurationRequest,
    ) -> TenantLLMConfiguration:

        configuration = (
            self.get_profile(
                db=db,
                tenant_id=tenant_id,
                configuration_id=
                    configuration_id,
            )
        )

        update_data = (
            payload.model_dump(
                exclude_unset=True,
                exclude_none=True,
            )
        )

        for (
            field,
            value,
        ) in update_data.items():

            setattr(
                configuration,
                field,
                value,
            )

        db.commit()
        db.refresh(
            configuration,
        )

        return configuration

    def set_default(
        self,
        db: Session,
        tenant_id: UUID,
        configuration_id: UUID,
    ) -> TenantLLMConfiguration:

        configuration = (
            self.get_profile(
                db=db,
                tenant_id=tenant_id,
                configuration_id=
                    configuration_id,
            )
        )

        if not configuration.is_active:
            raise ValueError(
                "Inactive LLM configuration "
                "cannot be made default."
            )

        self.repository.clear_default(
            db=db,
            tenant_id=tenant_id,
        )

        configuration.is_default = True

        db.commit()
        db.refresh(
            configuration,
        )

        return configuration

    def delete_profile(
        self,
        db: Session,
        tenant_id: UUID,
        configuration_id: UUID,
    ) -> None:

        configuration = (
            self.get_profile(
                db=db,
                tenant_id=tenant_id,
                configuration_id=
                    configuration_id,
            )
        )

        if configuration.is_default:
            raise ValueError(
                "Default LLM configuration "
                "cannot be deleted."
            )

        for knowledge_base in (
            configuration.knowledge_bases
        ):
            knowledge_base.llm_configuration_id = (
                None
            )

        db.delete(
            configuration,
        )

        db.commit()

    def assign_to_knowledge_base(
        self,
        db: Session,
        tenant_id: UUID,
        knowledge_base_id: UUID,
        configuration_id:
            UUID | None,
    ) -> KnowledgeBase:

        knowledge_base = db.get(
            KnowledgeBase,
            knowledge_base_id,
        )

        if (
            knowledge_base is None
            or knowledge_base.tenant_id
            != tenant_id
        ):
            raise ValueError(
                "Knowledge base not found."
            )

        if configuration_id is None:
            knowledge_base.llm_configuration_id = (
                None
            )

            db.commit()
            db.refresh(
                knowledge_base,
            )

            return knowledge_base

        configuration = (
            self.get_profile(
                db=db,
                tenant_id=tenant_id,
                configuration_id=
                    configuration_id,
            )
        )

        if not configuration.is_active:
            raise ValueError(
                "Inactive LLM configuration "
                "cannot be assigned."
            )

        knowledge_base.llm_configuration_id = (
            configuration.id
        )

        db.commit()
        db.refresh(
            knowledge_base,
        )

        return knowledge_base

    # Compatibility with old code.
    def get_active_configuration(
        self,
        db: Session,
        tenant_id: UUID,
    ) -> (
        TenantLLMConfiguration
        | None
    ):

        return (
            self.get_default_configuration(
                db=db,
                tenant_id=tenant_id,
            )
        )