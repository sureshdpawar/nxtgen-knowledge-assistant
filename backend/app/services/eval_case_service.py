from uuid import UUID

from sqlalchemy.orm import Session

from app.models.document import (
    Document,
)
from app.models.document_chunk import (
    DocumentChunk,
)
from app.models.eval_case import (
    EvalCase,
)
from app.models.eval_dataset import (
    EvalDataset,
)
from app.repositories.eval_case_repository import (
    EvalCaseRepository,
)
from app.schemas.eval import (
    EvalCaseCreate,
)


class EvalCaseService:

    def __init__(self):
        self.repository = (
            EvalCaseRepository()
        )

    def create(
        self,
        db: Session,
        payload: EvalCaseCreate,
    ) -> EvalCase:
        dataset = db.get(
            EvalDataset,
            payload.dataset_id,
        )

        if dataset is None:
            raise ValueError(
                "Eval dataset not found."
            )

        expected_document = None
        expected_chunk = None

        #
        # Validate expected document.
        #
        if (
            payload.expected_document_id
            is not None
        ):
            expected_document = db.get(
                Document,
                payload.expected_document_id,
            )

            if expected_document is None:
                raise ValueError(
                    "Expected document "
                    "not found."
                )

            document_kb_id = (
                expected_document
                .knowledge_source
                .knowledge_base_id
            )

            if (
                document_kb_id
                != dataset.knowledge_base_id
            ):
                raise ValueError(
                    "Expected document does "
                    "not belong to the Eval "
                    "dataset Knowledge Base."
                )

        #
        # Validate expected chunk.
        #
        if (
            payload.expected_chunk_id
            is not None
        ):
            expected_chunk = db.get(
                DocumentChunk,
                payload.expected_chunk_id,
            )

            if expected_chunk is None:
                raise ValueError(
                    "Expected chunk "
                    "not found."
                )

            chunk_document = (
                expected_chunk.document
            )

            chunk_kb_id = (
                chunk_document
                .knowledge_source
                .knowledge_base_id
            )

            if (
                chunk_kb_id
                != dataset.knowledge_base_id
            ):
                raise ValueError(
                    "Expected chunk does "
                    "not belong to the Eval "
                    "dataset Knowledge Base."
                )

            #
            # If both expected_document_id
            # and expected_chunk_id were
            # provided, they must refer to
            # the same document.
            #
            if (
                expected_document
                is not None
                and expected_chunk.document_id
                != expected_document.id
            ):
                raise ValueError(
                    "Expected chunk does "
                    "not belong to the "
                    "expected document."
                )

        #
        # Validate portable expected sources.
        #
        # For V1 we support URL-based sources.
        #
        # We do not resolve the URL to a
        # document here because the purpose
        # of expected_sources is portability
        # across environments.
        #
        expected_sources = []

        for source in payload.expected_sources:
            source_type = (
                source.type
                .strip()
                .lower()
            )

            source_value = (
                source.value
                .strip()
            )

            if not source_value:
                raise ValueError(
                    "Expected source value "
                    "cannot be empty."
                )

            if source_type not in {
                "url",
                "external_id",
            }:
                raise ValueError(
                    "Unsupported expected "
                    "source type: "
                    f"{source.type}"
                )

            expected_sources.append(
                {
                    "type":
                        source_type,

                    "value":
                        source_value,
                }
            )

        #
        # Basic golden-case validation.
        #
        if (
            payload.answerable
            and not payload.expected_answer
        ):
            raise ValueError(
                "Answerable evaluation "
                "cases should have an "
                "expected answer."
            )

        eval_case = EvalCase(
            dataset_id=
                payload.dataset_id,

            question=
                payload.question,

            expected_document_id=
                payload.expected_document_id,

            expected_chunk_id=
                payload.expected_chunk_id,

            expected_sources=
                expected_sources,

            expected_text=
                payload.expected_text,

            expected_answer=
                payload.expected_answer,

            answerable=
                payload.answerable,
        )

        eval_case = (
            self.repository.create(
                db=db,
                entity=eval_case,
            )
        )

        db.commit()

        db.refresh(
            eval_case
        )

        return eval_case

    def get(
        self,
        db: Session,
        eval_case_id: UUID,
    ) -> EvalCase | None:
        return (
            self.repository.get(
                db=db,
                entity_id=
                    eval_case_id,
            )
        )

    def list_by_dataset_id(
        self,
        db: Session,
        dataset_id: UUID,
    ) -> list[EvalCase]:
        return (
            self.repository
            .list_by_dataset_id(
                db=db,
                dataset_id=
                    dataset_id,
            )
        )