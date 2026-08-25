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
from app.models.knowledge_base import (
    KnowledgeBase,
)
from app.schemas.eval import (
    EvalDatasetImportPayload,
)


class EvalDatasetImportService:

    def import_dataset(
        self,
        db: Session,
        payload: EvalDatasetImportPayload,
    ) -> tuple[
        EvalDataset,
        int,
    ]:
        """
        Import one complete evaluation dataset
        and all of its cases in a single
        transaction.

        If any case is invalid, the entire
        import is rolled back.
        """

        knowledge_base = db.get(
            KnowledgeBase,
            payload.knowledge_base_id,
        )

        if knowledge_base is None:
            raise ValueError(
                "Knowledge Base not found."
            )

        if not payload.cases:
            raise ValueError(
                "Evaluation dataset must "
                "contain at least one case."
            )

        try:
            #
            # Create dataset.
            #
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

            db.add(
                dataset
            )

            #
            # Flush so dataset.id exists
            # without committing yet.
            #
            db.flush()

            case_count = 0

            for (
                index,
                case_payload,
            ) in enumerate(
                payload.cases,
                start=1,
            ):
                #
                # Validate expected document
                # when supplied.
                #
                expected_document = None

                if (
                    case_payload
                    .expected_document_id
                    is not None
                ):
                    expected_document = db.get(
                        Document,
                        case_payload
                        .expected_document_id,
                    )

                    if expected_document is None:
                        raise ValueError(
                            "Case "
                            f"{index}: expected "
                            "document not found."
                        )

                    document_kb_id = (
                        expected_document
                        .knowledge_source
                        .knowledge_base_id
                    )

                    if (
                        document_kb_id
                        != payload
                        .knowledge_base_id
                    ):
                        raise ValueError(
                            "Case "
                            f"{index}: expected "
                            "document does not "
                            "belong to the "
                            "Knowledge Base."
                        )

                #
                # Validate expected chunk
                # when supplied.
                #
                expected_chunk = None

                if (
                    case_payload
                    .expected_chunk_id
                    is not None
                ):
                    expected_chunk = db.get(
                        DocumentChunk,
                        case_payload
                        .expected_chunk_id,
                    )

                    if expected_chunk is None:
                        raise ValueError(
                            "Case "
                            f"{index}: expected "
                            "chunk not found."
                        )

                    chunk_document = (
                        expected_chunk
                        .document
                    )

                    chunk_kb_id = (
                        chunk_document
                        .knowledge_source
                        .knowledge_base_id
                    )

                    if (
                        chunk_kb_id
                        != payload
                        .knowledge_base_id
                    ):
                        raise ValueError(
                            "Case "
                            f"{index}: expected "
                            "chunk does not "
                            "belong to the "
                            "Knowledge Base."
                        )

                    #
                    # If both IDs exist they
                    # must refer to the same
                    # document.
                    #
                    if (
                        expected_document
                        is not None
                        and
                        expected_chunk
                        .document_id
                        != expected_document.id
                    ):
                        raise ValueError(
                            "Case "
                            f"{index}: expected "
                            "chunk does not "
                            "belong to expected "
                            "document."
                        )

                #
                # Validate portable expected
                # sources.
                #
                expected_sources = []

                for source in (
                    case_payload
                    .expected_sources
                ):
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
                            "Case "
                            f"{index}: expected "
                            "source value cannot "
                            "be empty."
                        )

                    if source_type not in {
                        "url",
                        "external_id",
                    }:
                        raise ValueError(
                            "Case "
                            f"{index}: unsupported "
                            "expected source type: "
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
                # Basic quality validation.
                #
                if (
                    case_payload.answerable
                    and
                    not case_payload
                    .expected_answer
                ):
                    raise ValueError(
                        "Case "
                        f"{index}: answerable "
                        "cases should have an "
                        "expected_answer."
                    )

                #
                # Create case.
                #
                eval_case = EvalCase(
                    dataset_id=
                        dataset.id,

                    question=
                        case_payload.question,

                    expected_document_id=
                        case_payload
                        .expected_document_id,

                    expected_chunk_id=
                        case_payload
                        .expected_chunk_id,

                    expected_sources=
                        expected_sources,

                    expected_text=
                        case_payload
                        .expected_text,

                    expected_answer=
                        case_payload
                        .expected_answer,

                    answerable=
                        case_payload
                        .answerable,
                )

                db.add(
                    eval_case
                )

                case_count += 1

            #
            # Everything succeeded.
            #
            db.commit()

            db.refresh(
                dataset
            )

            return (
                dataset,
                case_count,
            )

        except Exception:
            db.rollback()
            raise