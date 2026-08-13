# app/schemas/user.py

from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
)

from app.core.enums import UserRole


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class TenantAdminCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class TenantAdminUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: UUID
    tenant_id: UUID | None

    first_name: str
    last_name: str
    email: EmailStr

    role: UserRole
    is_active: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class UserLogin(BaseModel):
    email: EmailStr
    password: str