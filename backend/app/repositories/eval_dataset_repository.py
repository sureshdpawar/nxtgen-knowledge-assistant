from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.eval_dataset import (
    EvalDataset,
)
from app.repositories.base_repository import (
    BaseRepository,
)


class EvalDatasetRepository(
    BaseRepository[
        EvalDataset
    ],
):

    def __init__(self):
        super().__init__(
            EvalDataset,
        )

    def list_by_knowledge_base_id(
        self,
        db: Session,
        knowledge_base_id: UUID,
    ) -> list[EvalDataset]:
        stmt = (
            select(
                EvalDataset
            )
            .where(
                EvalDataset
                .knowledge_base_id
                == knowledge_base_id
            )
            .order_by(
                EvalDataset
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