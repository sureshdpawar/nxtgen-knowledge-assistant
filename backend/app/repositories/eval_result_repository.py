from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.eval_result import (
    EvalResult,
)
from app.repositories.base_repository import (
    BaseRepository,
)


class EvalResultRepository(
    BaseRepository[
        EvalResult
    ],
):

    def __init__(self):
        super().__init__(
            EvalResult,
        )

    def list_by_experiment_id(
        self,
        db: Session,
        experiment_id: UUID,
    ) -> list[EvalResult]:
        stmt = (
            select(
                EvalResult
            )
            .where(
                EvalResult.experiment_id
                == experiment_id
            )
            .order_by(
                EvalResult
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