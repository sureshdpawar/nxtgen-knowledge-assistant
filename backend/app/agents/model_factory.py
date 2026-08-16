from langchain_openai import (
    ChatOpenAI,
)

from app.core.enums import LLMProvider
from app.models.tenant_llm_configuration import (
    TenantLLMConfiguration,
)


class AgentModelFactory:

    def create(
        self,
        configuration:
            TenantLLMConfiguration,
    ):

        if (
            configuration.provider
            == LLMProvider.OPENAI
        ):
            return ChatOpenAI(
                model=
                    configuration.model_name,

                api_key=
                    configuration.api_key,

                base_url=
                    configuration.base_url,

                temperature=
                    configuration.temperature,

                max_tokens=
                    configuration.max_tokens,
            )

        raise ValueError(
            "Agent runtime does not yet "
            "support LLM provider "
            f"'{configuration.provider.value}'."
        )