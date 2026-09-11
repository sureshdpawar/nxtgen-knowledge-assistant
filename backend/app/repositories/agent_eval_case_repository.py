from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.agent_eval_case import AgentEvalCase
from app.repositories.base_repository import BaseRepository


class AgentEvalCaseRepository(
    BaseRepository[AgentEvalCase],
):
    def __init__(self):
        super().__init__(AgentEvalCase)

    def list_by_dataset_id(
        self,
        db: Session,
        dataset_id: UUID,
    ) -> list[AgentEvalCase]:
        stmt = (
            select(AgentEvalCase)
            .where(
                AgentEvalCase.dataset_id == dataset_id
            )
            .order_by(
                AgentEvalCase.created_at.asc()
            )
        )

        return list(
            db.execute(stmt).scalars().all()
        )
