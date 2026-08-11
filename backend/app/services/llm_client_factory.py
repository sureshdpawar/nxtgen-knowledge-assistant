from uuid import UUID

from openai import OpenAI
from sqlalchemy.orm import Session

from app.core.enums import LLMProvider
from app.models.tenant_llm_configuration import (
    TenantLLMConfiguration,
)
from app.repositories.tenant_llm_configuration_repository import (
    TenantLLMConfigurationRepository,
)


class LLMClientFactory:

    def __init__(self):
        self.repository = (
            TenantLLMConfigurationRepository()
        )

    def create(
        self,
        db: Session,
        tenant_id: UUID,
    ) -> tuple[OpenAI, TenantLLMConfiguration]:

        config = self.repository.get_active_by_tenant_id(
            db=db,
            tenant_id=tenant_id,
        )

        if config is None:
            raise ValueError(
                "No active LLM configuration found."
            )

        if config.provider in (
            LLMProvider.OPENAI,
            LLMProvider.AZURE_OPENAI,
            LLMProvider.VLLM,
        ):
            client = OpenAI(
                api_key=config.api_key,
                base_url=config.base_url,
            )

            return (
                client,
                config,
            )

        raise NotImplementedError(
            f"LLM provider '{config.provider.value}' is not supported."
        )