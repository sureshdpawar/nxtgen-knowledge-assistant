from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.agent_eval_dataset import AgentEvalDataset
from app.repositories.base_repository import BaseRepository


class AgentEvalDatasetRepository(
    BaseRepository[AgentEvalDataset],
):
    def __init__(self):
        super().__init__(AgentEvalDataset)

    def list_by_tenant_id(
        self,
        db: Session,
        tenant_id: UUID,
        agent_id: UUID | None = None,
    ) -> list[AgentEvalDataset]:
        stmt = select(AgentEvalDataset).where(
            AgentEvalDataset.tenant_id == tenant_id
        )

        if agent_id is not None:
            stmt = stmt.where(
                AgentEvalDataset.agent_id == agent_id
            )

        stmt = stmt.order_by(
            AgentEvalDataset.created_at.desc()
        )

        return list(
            db.execute(stmt).scalars().all()
        )
