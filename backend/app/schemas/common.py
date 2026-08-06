from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UUIDSchema(BaseSchema):
    id: UUID


class TimestampSchema(BaseSchema):
    created_at: datetime
    updated_at: datetime