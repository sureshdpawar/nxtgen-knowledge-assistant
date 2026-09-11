from uuid import UUID

from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.agent_eval_dataset import AgentEvalDataset
from app.models.user import User
from app.repositories.agent_eval_dataset_repository import (
    AgentEvalDatasetRepository,
)
from app.schemas.agent_eval import AgentEvalDatasetCreate


class AgentEvalDatasetService:
    def __init__(self):
        self.repository = AgentEvalDatasetRepository()

    @staticmethod
    def _tenant_id(current_user: User) -> UUID:
        if current_user.tenant_id is None:
            raise ValueError(
                "Agent Evaluation requires a tenant-scoped admin."
            )
        return current_user.tenant_id

    def create(
        self,
        db: Session,
        current_user: User,
        payload: AgentEvalDatasetCreate,
    ) -> AgentEvalDataset:
        tenant_id = self._tenant_id(current_user)

        agent = db.get(Agent, payload.agent_id)
        if agent is None or agent.tenant_id != tenant_id:
            raise ValueError("Agent not found.")

        dataset = AgentEvalDataset(
            tenant_id=tenant_id,
            agent_id=payload.agent_id,
            name=payload.name.strip(),
            version=payload.version.strip(),
            description=payload.description,
        )

        dataset = self.repository.create(
            db=db,
            entity=dataset,
        )
        db.commit()
        db.refresh(dataset)
        return dataset

    def get(
        self,
        db: Session,
        current_user: User,
        dataset_id: UUID,
    ) -> AgentEvalDataset | None:
        tenant_id = self._tenant_id(current_user)
        dataset = self.repository.get(
            db=db,
            entity_id=dataset_id,
        )

        if dataset is None or dataset.tenant_id != tenant_id:
            return None

        return dataset

    def list(
        self,
        db: Session,
        current_user: User,
        agent_id: UUID | None = None,
    ) -> list[AgentEvalDataset]:
        tenant_id = self._tenant_id(current_user)

        if agent_id is not None:
            agent = db.get(Agent, agent_id)
            if agent is None or agent.tenant_id != tenant_id:
                raise ValueError("Agent not found.")

        return self.repository.list_by_tenant_id(
            db=db,
            tenant_id=tenant_id,
            agent_id=agent_id,
        )
