from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.eval_case import (
    EvalCase,
)
from app.repositories.base_repository import (
    BaseRepository,
)


class EvalCaseRepository(
    BaseRepository[
        EvalCase
    ],
):

    def __init__(self):
        super().__init__(
            EvalCase,
        )

    def list_by_dataset_id(
        self,
        db: Session,
        dataset_id: UUID,
    ) -> list[EvalCase]:
        stmt = (
            select(
                EvalCase
            )
            .where(
                EvalCase.dataset_id
                == dataset_id
            )
            .order_by(
                EvalCase
                .created_at
                .asc()
            )
        )

        return list(
            db.execute(
                stmt
            )
            .scalars()
            .all()
        )