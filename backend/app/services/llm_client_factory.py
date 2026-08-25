import logging

from uuid import UUID

from openai import OpenAI
from sqlalchemy.orm import Session

from app.core.enums import (
    LLMProvider,
)
from app.exceptions.llm import (
    LLMConfigurationNotFoundError,
)
from app.models.knowledge_base import (
    KnowledgeBase,
)
from app.models.tenant_llm_configuration import (
    TenantLLMConfiguration,
)
from app.repositories.tenant_llm_configuration_repository import (
    TenantLLMConfigurationRepository,
)


logger = logging.getLogger(
    "nxtgen.llm"
)


class LLMClientFactory:

    def __init__(self):
        self.repository = (
            TenantLLMConfigurationRepository()
        )

    def _build_client(
        self,
        config:
            TenantLLMConfiguration,
    ) -> OpenAI:

        if config.provider in (
            LLMProvider.OPENAI,
            LLMProvider.AZURE_OPENAI,
            LLMProvider.VLLM,
        ):
            return OpenAI(
                api_key=
                    config.api_key,

                base_url=
                    config.base_url,
            )

        raise NotImplementedError(
            "LLM provider "
            f"'{config.provider.value}' "
            "is not supported."
        )

    def create_for_configuration(
        self,
        db: Session,
        tenant_id: UUID,
        configuration_id: UUID,
    ) -> tuple[
        OpenAI,
        TenantLLMConfiguration,
    ]:
        """
        Resolve one explicit tenant LLM profile.

        Evaluation uses this so the evaluator
        model can be different from the model
        being evaluated.
        """

        configuration = (
            self.repository
            .get_by_id_and_tenant(
                db=db,

                tenant_id=
                    tenant_id,

                configuration_id=
                    configuration_id,
            )
        )

        if configuration is None:
            raise ValueError(
                "LLM configuration not found."
            )

        if not configuration.is_active:
            raise ValueError(
                "LLM configuration is inactive."
            )

        logger.info(
            "Resolved explicit LLM profile "
            "'%s' (%s), model '%s', "
            "provider '%s' for tenant %s",
            configuration.name,
            configuration.id,
            configuration.model_name,
            configuration.provider.value,
            tenant_id,
        )

        client = (
            self._build_client(
                configuration
            )
        )

        return (
            client,
            configuration,
        )

    def create_for_knowledge_base(
        self,
        db: Session,
        tenant_id: UUID,
        knowledge_base_id: UUID,
    ) -> tuple[
        OpenAI,
        TenantLLMConfiguration,
    ]:

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

        configuration = None

        resolution_source = (
            "tenant_default"
        )

        if (
            knowledge_base
            .llm_configuration_id
            is not None
        ):
            configuration = (
                self.repository
                .get_by_id_and_tenant(
                    db=db,

                    tenant_id=
                        tenant_id,

                    configuration_id=
                        knowledge_base
                        .llm_configuration_id,
                )
            )

            if (
                configuration is not None
                and configuration.is_active
            ):
                resolution_source = (
                    "knowledge_base_override"
                )

            elif (
                configuration is not None
                and not configuration.is_active
            ):
                logger.warning(
                    "Inactive LLM profile "
                    "'%s' (%s) assigned "
                    "to KB %s; falling "
                    "back to tenant default",
                    configuration.name,
                    configuration.id,
                    knowledge_base.id,
                )

                configuration = None

        if configuration is None:
            configuration = (
                self.repository
                .get_default_by_tenant_id(
                    db=db,

                    tenant_id=
                        tenant_id,
                )
            )

            resolution_source = (
                "tenant_default"
            )

        if configuration is None:
            logger.error(
                "No active LLM "
                "configuration available "
                "tenant=%s kb=%s",
                tenant_id,
                knowledge_base_id,
            )

            raise (
                LLMConfigurationNotFoundError()
            )

        logger.info(
            "Resolved LLM profile "
            "'%s' (%s), model '%s', "
            "provider '%s' for KB %s "
            "using %s",
            configuration.name,
            configuration.id,
            configuration.model_name,
            configuration.provider.value,
            knowledge_base.id,
            resolution_source,
        )

        client = (
            self._build_client(
                configuration
            )
        )

        return (
            client,
            configuration,
        )

    def create(
        self,
        db: Session,
        tenant_id: UUID,
    ) -> tuple[
        OpenAI,
        TenantLLMConfiguration,
    ]:
        """
        Resolve tenant default profile.

        Existing compatibility method and
        also the default evaluator fallback.
        """

        configuration = (
            self.repository
            .get_default_by_tenant_id(
                db=db,

                tenant_id=
                    tenant_id,
            )
        )

        if configuration is None:
            logger.error(
                "No active tenant "
                "default LLM profile "
                "tenant=%s",
                tenant_id,
            )

            raise (
                LLMConfigurationNotFoundError()
            )

        logger.info(
            "Resolved tenant default "
            "LLM profile '%s' (%s), "
            "model '%s', provider '%s' "
            "for tenant %s",
            configuration.name,
            configuration.id,
            configuration.model_name,
            configuration.provider.value,
            tenant_id,
        )

        client = (
            self._build_client(
                configuration
            )
        )

        return (
            client,
            configuration,
        )