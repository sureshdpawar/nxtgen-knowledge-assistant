from __future__ import annotations

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(Generic[T]):

    def __init__(self, model: type[T]):
        self.model = model

    def get(
        self,
        db: Session,
        entity_id: UUID,
    ) -> T | None:
        return db.get(self.model, entity_id)

    def get_by(
        self,
        db: Session,
        **filters: Any,
    ) -> T | None:
        stmt = (
            select(self.model)
            .filter_by(**filters)
        )

        return db.execute(stmt).scalars().first()

    def list(
        self,
        db: Session,
    ) -> list[T]:
        stmt = select(self.model)

        return db.execute(stmt).scalars().all()

    def filter_by(
        self,
        db: Session,
        **filters: Any,
    ) -> list[T]:
        stmt = (
            select(self.model)
            .filter_by(**filters)
        )

        return db.execute(stmt).scalars().all()

    def exists(
        self,
        db: Session,
        **filters: Any,
    ) -> bool:
        return self.get_by(
            db,
            **filters,
        ) is not None

    def count_by(
        self,
        db: Session,
        **filters: Any,
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(self.model)
            .filter_by(**filters)
        )

        return db.scalar(stmt) or 0

    def create(
        self,
        db: Session,
        entity: T,
    ) -> T:
        db.add(entity)
        db.flush()
        db.refresh(entity)

        return entity

    def update(
        self,
        db: Session,
        entity: T,
    ) -> T:
        db.flush()
        db.refresh(entity)

        return entity

    def delete(
        self,
        db: Session,
        entity: T,
    ) -> None:
        db.delete(entity)