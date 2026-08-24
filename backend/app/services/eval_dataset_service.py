from uuid import UUID

from sqlalchemy.orm import Session

from app.models.eval_dataset import (
    EvalDataset,
)
from app.models.knowledge_base import (
    KnowledgeBase,
)
from app.repositories.eval_dataset_repository import (
    EvalDatasetRepository,
)
from app.schemas.eval import (
    EvalDatasetCreate,
)


class EvalDatasetService:

    def __init__(self):
        self.repository = (
            EvalDatasetRepository()
        )

    def create(
        self,
        db: Session,
        payload: EvalDatasetCreate,
    ) -> EvalDataset:
        knowledge_base = db.get(
            KnowledgeBase,
            payload.knowledge_base_id,
        )

        if knowledge_base is None:
            raise ValueError(
                "Knowledge Base not found."
            )

        dataset = EvalDataset(
            knowledge_base_id=
                payload.knowledge_base_id,
            name=
                payload.name,
            version=
                payload.version,
            description=
                payload.description,
        )

        dataset = self.repository.create(
            db=db,
            entity=dataset,
        )

        db.commit()
        db.refresh(
            dataset
        )

        return dataset

    def get(
        self,
        db: Session,
        dataset_id: UUID,
    ) -> EvalDataset | None:
        return self.repository.get(
            db=db,
            entity_id=dataset_id,
        )

    def list_by_knowledge_base_id(
        self,
        db: Session,
        knowledge_base_id: UUID,
    ) -> list[EvalDataset]:
        return (
            self.repository
            .list_by_knowledge_base_id(
                db=db,
                knowledge_base_id=
                    knowledge_base_id,
            )
        )