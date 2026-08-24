from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class UsageLimitCreate(
    BaseModel
):
    tenant_id: UUID

    knowledge_base_id: (
        UUID | None
    ) = None

    chat_channel_id: (
        UUID | None
    ) = None

    daily_message_limit: (
        int | None
    ) = Field(
        default=None,
        ge=0,
    )

    daily_input_token_limit: (
        int | None
    ) = Field(
        default=None,
        ge=0,
    )

    daily_output_token_limit: (
        int | None
    ) = Field(
        default=None,
        ge=0,
    )

    daily_total_token_limit: (
        int | None
    ) = Field(
        default=None,
        ge=0,
    )

    monthly_message_limit: (
        int | None
    ) = Field(
        default=None,
        ge=0,
    )

    monthly_input_token_limit: (
        int | None
    ) = Field(
        default=None,
        ge=0,
    )

    monthly_output_token_limit: (
        int | None
    ) = Field(
        default=None,
        ge=0,
    )

    monthly_total_token_limit: (
        int | None
    ) = Field(
        default=None,
        ge=0,
    )

    max_input_tokens_per_request: (
        int | None
    ) = Field(
        default=None,
        ge=0,
    )

    max_output_tokens_per_request: (
        int | None
    ) = Field(
        default=None,
        ge=0,
    )

    timezone: str = Field(
        default="UTC",
        min_length=1,
        max_length=100,
    )

    enabled: bool = True


class UsageLimitUpdate(
    BaseModel
):
    daily_message_limit: (
        int | None
    ) = Field(
        default=None,
        ge=0,
    )

    daily_input_token_limit: (
        int | None
    ) = Field(
        default=None,
        ge=0,
    )

    daily_output_token_limit: (
        int | None
    ) = Field(
        default=None,
        ge=0,
    )

    daily_total_token_limit: (
        int | None
    ) = Field(
        default=None,
        ge=0,
    )

    monthly_message_limit: (
        int | None
    ) = Field(
        default=None,
        ge=0,
    )

    monthly_input_token_limit: (
        int | None
    ) = Field(
        default=None,
        ge=0,
    )

    monthly_output_token_limit: (
        int | None
    ) = Field(
        default=None,
        ge=0,
    )

    monthly_total_token_limit: (
        int | None
    ) = Field(
        default=None,
        ge=0,
    )

    max_input_tokens_per_request: (
        int | None
    ) = Field(
        default=None,
        ge=0,
    )

    max_output_tokens_per_request: (
        int | None
    ) = Field(
        default=None,
        ge=0,
    )

    timezone: (
        str | None
    ) = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    enabled: (
        bool | None
    ) = None


class UsageLimitResponse(
    BaseModel
):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    tenant_id: UUID

    knowledge_base_id: (
        UUID | None
    )

    chat_channel_id: (
        UUID | None
    )

    daily_message_limit: (
        int | None
    )

    daily_input_token_limit: (
        int | None
    )

    daily_output_token_limit: (
        int | None
    )

    daily_total_token_limit: (
        int | None
    )

    monthly_message_limit: (
        int | None
    )

    monthly_input_token_limit: (
        int | None
    )

    monthly_output_token_limit: (
        int | None
    )

    monthly_total_token_limit: (
        int | None
    )

    max_input_tokens_per_request: (
        int | None
    )

    max_output_tokens_per_request: (
        int | None
    )

    timezone: str

    enabled: bool