from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.enums import LLMProvider


class TenantLLMConfigurationResponse(
    BaseModel,
):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    provider: LLMProvider

    model_name: str

    base_url: str

    api_key: str

    temperature: float

    max_tokens: int

    is_active: bool


class UpdateTenantLLMConfigurationRequest(
    BaseModel,
):
    provider: LLMProvider

    model_name: str

    base_url: str

    api_key: str

    temperature: float

    max_tokens: int

    is_active: bool = True