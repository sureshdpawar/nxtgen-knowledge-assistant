from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.enums import LLMProvider


class TenantLLMConfigurationResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    name: str
    provider: LLMProvider
    model_name: str
    base_url: str
    temperature: float
    max_tokens: int
    is_active: bool
    is_default: bool


class CreateTenantLLMConfigurationRequest(BaseModel):
    name: str
    provider: LLMProvider
    model_name: str
    base_url: str
    api_key: str
    temperature: float = 0.0
    max_tokens: int = 2048
    is_active: bool = True
    is_default: bool = False


class UpdateTenantLLMConfigurationRequest(BaseModel):
    name: str | None = None
    provider: LLMProvider | None = None
    model_name: str | None = None
    base_url: str | None = None
    api_key: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    is_active: bool | None = None


class KnowledgeBaseLLMConfigurationRequest(BaseModel):
    llm_configuration_id: UUID | None