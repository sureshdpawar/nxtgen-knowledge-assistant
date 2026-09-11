from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.agent_eval_experiment import AgentEvalExperiment
from app.repositories.base_repository import BaseRepository


class AgentEvalExperimentRepository(BaseRepository[AgentEvalExperiment]):
    def __init__(self):
        super().__init__(AgentEvalExperiment)

    def list_by_tenant_id(
        self,
        db: Session,
        tenant_id: UUID,
        dataset_id: UUID | None = None,
    ) -> list[AgentEvalExperiment]:
        stmt = select(AgentEvalExperiment).where(
            AgentEvalExperiment.tenant_id == tenant_id
        )
        if dataset_id is not None:
            stmt = stmt.where(AgentEvalExperiment.dataset_id == dataset_id)
        stmt = stmt.order_by(AgentEvalExperiment.created_at.desc())
        return list(db.execute(stmt).scalars().all())
