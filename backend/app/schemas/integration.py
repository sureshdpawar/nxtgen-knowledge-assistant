from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.core.enums import (
    IntegrationAuthType,
    IntegrationType,
)


class IntegrationCreate(
    BaseModel,
):
    name: str = Field(
        min_length=1,
        max_length=255,
    )

    integration_type: IntegrationType

    base_url: str = Field(
        min_length=1,
        max_length=2000,
    )

    auth_type: IntegrationAuthType = (
        IntegrationAuthType.NONE
    )

    auth_config: dict | None = None

    configuration: dict | None = None

    is_active: bool = True


class IntegrationUpdate(
    BaseModel,
):
    name: str | None = None

    base_url: str | None = None

    auth_type:IntegrationAuthType | None = None

    auth_config:dict | None = None

    configuration:dict | None = None

    is_active:bool | None = None


class IntegrationResponse(
    BaseModel,
):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    tenant_id: UUID

    name: str

    integration_type:IntegrationType

    base_url: str

    auth_type:IntegrationAuthType

    configuration: dict | None

    is_active: bool

    created_at: datetime
    updated_at: datetime