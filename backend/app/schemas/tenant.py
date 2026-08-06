from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TenantCreate(BaseModel):
    name: str
    slug: str


class TenantUpdate(BaseModel):
    name: str | None = None
    plan: str | None = None
    status: str | None = None


class TenantResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    plan: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)