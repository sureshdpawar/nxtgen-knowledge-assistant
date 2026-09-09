from uuid import UUID

from sqlalchemy.orm import Session

from app.models.agent_eval_case import AgentEvalCase
from app.models.user import User
from app.repositories.agent_eval_case_repository import (
    AgentEvalCaseRepository,
)
from app.schemas.agent_eval import AgentEvalCaseCreate
from app.services.agent_eval_dataset_service import (
    AgentEvalDatasetService,
)


class AgentEvalCaseService:
    def __init__(self):
        self.repository = AgentEvalCaseRepository()
        self.dataset_service = AgentEvalDatasetService()

    def create(
        self,
        db: Session,
        current_user: User,
        dataset_id: UUID,
        payload: AgentEvalCaseCreate,
    ) -> AgentEvalCase:
        dataset = self.dataset_service.get(
            db=db,
            current_user=current_user,
            dataset_id=dataset_id,
        )
        if dataset is None:
            raise ValueError("Agent Evaluation dataset not found.")

        expected_tools = [
            tool.model_dump()
            for tool in payload.expected_tools
        ]

        forbidden_tools = [
            name.strip()
            for name in payload.forbidden_tools
            if name.strip()
        ]

        case = AgentEvalCase(
            dataset_id=dataset.id,
            name=payload.name.strip(),
            input=payload.input.strip(),
            expected_outcome=payload.expected_outcome.strip(),
            expected_tools=expected_tools,
            forbidden_tools=forbidden_tools,
            enabled=payload.enabled,
        )

        case = self.repository.create(
            db=db,
            entity=case,
        )
        db.commit()
        db.refresh(case)
        return case

    def list(
        self,
        db: Session,
        current_user: User,
        dataset_id: UUID,
    ) -> list[AgentEvalCase]:
        dataset = self.dataset_service.get(
            db=db,
            current_user=current_user,
            dataset_id=dataset_id,
        )
        if dataset is None:
            raise ValueError("Agent Evaluation dataset not found.")

        return self.repository.list_by_dataset_id(
            db=db,
            dataset_id=dataset.id,
        )

    def delete(
        self,
        db: Session,
        current_user: User,
        dataset_id: UUID,
        case_id: UUID,
    ) -> None:
        dataset = self.dataset_service.get(
            db=db,
            current_user=current_user,
            dataset_id=dataset_id,
        )
        if dataset is None:
            raise ValueError("Agent Evaluation dataset not found.")

        case = self.repository.get(
            db=db,
            entity_id=case_id,
        )
        if case is None or case.dataset_id != dataset.id:
            raise ValueError("Agent Evaluation case not found.")

        db.delete(case)
        db.commit()
