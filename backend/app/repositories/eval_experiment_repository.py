from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.eval_experiment import (
    EvalExperiment,
)
from app.repositories.base_repository import (
    BaseRepository,
)


class EvalExperimentRepository(
    BaseRepository[
        EvalExperiment
    ],
):

    def __init__(self):
        super().__init__(
            EvalExperiment,
        )

    def list_by_dataset_id(
        self,
        db: Session,
        dataset_id: UUID,
    ) -> list[EvalExperiment]:
        stmt = (
            select(
                EvalExperiment
            )
            .where(
                EvalExperiment.dataset_id
                == dataset_id
            )
            .order_by(
                EvalExperiment
                .created_at
                .desc()
            )
        )

        return list(
            db.execute(
                stmt
            )
            .scalars()
            .all()
        )