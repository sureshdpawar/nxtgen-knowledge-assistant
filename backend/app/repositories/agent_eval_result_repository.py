from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.agent_eval_result import AgentEvalResult
from app.repositories.base_repository import BaseRepository


class AgentEvalResultRepository(BaseRepository[AgentEvalResult]):
    def __init__(self):
        super().__init__(AgentEvalResult)

    def list_by_experiment_id(
        self,
        db: Session,
        experiment_id: UUID,
    ) -> list[AgentEvalResult]:
        stmt = (
            select(AgentEvalResult)
            .where(AgentEvalResult.experiment_id == experiment_id)
            .order_by(AgentEvalResult.created_at.asc())
        )
        return list(db.execute(stmt).scalars().all())
