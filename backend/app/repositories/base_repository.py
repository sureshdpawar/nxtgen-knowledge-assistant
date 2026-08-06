from typing import Generic, TypeVar, Type
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: UUID):
        return db.get(self.model, id)

    def list(self, db: Session):
        return db.execute(
            select(self.model)
        ).scalars().all()

    def create(self, db: Session, obj: ModelType):
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db: Session, obj: ModelType):
        db.delete(obj)
        db.commit()