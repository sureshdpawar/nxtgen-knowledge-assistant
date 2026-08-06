from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(Generic[T]):

    def __init__(self, model: type[T]):
        self.model = model

    def get(self, db: Session, entity_id: UUID) -> T | None:
        return db.get(self.model, entity_id)

    def list(self, db: Session) -> list[T]:
        stmt = select(self.model)
        return db.execute(stmt).scalars().all()

    def create(self, db: Session, entity: T) -> T:
        db.add(entity)
        db.flush()
        db.refresh(entity)
        return entity

    def update(self, db: Session, entity: T) -> T:
        db.flush()
        db.refresh(entity)
        return entity

    def delete(self, db: Session, entity: T) -> None:
        db.delete(entity)