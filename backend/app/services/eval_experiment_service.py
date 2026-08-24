from uuid import UUID

from sqlalchemy.orm import Session

from app.core.constants import (
    EMBEDDING_MODEL,
)
from app.models.eval_dataset import (
    EvalDataset,
)
from app.models.eval_experiment import (
    EvalExperiment,
)
from app.models.eval_result import (
    EvalResult,
)
from app.repositories.eval_case_repository import (
    EvalCaseRepository,
)
from app.repositories.eval_experiment_repository import (
    EvalExperimentRepository,
)
from app.repositories.eval_result_repository import (
    EvalResultRepository,
)
from app.services.retrieval_eval_service import (
    RetrievalEvalService,
)


class EvalExperimentService:

    def __init__(self):
        self.experiment_repository = (
            EvalExperimentRepository()
        )

        self.case_repository = (
            EvalCaseRepository()
        )

        self.result_repository = (
            EvalResultRepository()
        )

        self.retrieval_eval_service = (
            RetrievalEvalService()
        )

    def run_retrieval_experiment(
        self,
        db: Session,
        dataset_id: UUID,
        knowledge_base_id: UUID,
        name: str,
        top_k: int,
    ) -> EvalExperiment:
        if top_k < 1:
            raise ValueError(
                "top_k must be "
                "greater than 0."
            )

        #
        # Validate dataset.
        #
        dataset = db.get(
            EvalDataset,
            dataset_id,
        )

        if dataset is None:
            raise ValueError(
                "Eval dataset "
                "not found."
            )

        #
        # The dataset must belong to the
        # Knowledge Base being evaluated.
        #
        # This prevents accidentally
        # evaluating questions from one KB
        # against another KB.
        #
        if (
            dataset.knowledge_base_id
            != knowledge_base_id
        ):
            raise ValueError(
                "Eval dataset does not "
                "belong to the supplied "
                "Knowledge Base."
            )

        cases = (
            self.case_repository
            .list_by_dataset_id(
                db=db,
                dataset_id=
                    dataset_id,
            )
        )

        if not cases:
            raise ValueError(
                "Eval dataset contains "
                "no cases."
            )

        experiment = EvalExperiment(
            dataset_id=
                dataset_id,
            knowledge_base_id=
                knowledge_base_id,
            name=
                name,
            eval_type=
                "retrieval",
            top_k=
                top_k,
            chunk_size=
                None,
            chunk_overlap=
                None,
            embedding_model=
                EMBEDDING_MODEL,
            llm_model=
                None,
            status=
                "running",
            metrics={},
        )

        experiment = (
            self.experiment_repository
            .create(
                db=db,
                entity=experiment,
            )
        )

        db.commit()

        db.refresh(
            experiment
        )

        case_results = []

        try:
            for eval_case in cases:
                result_data = (
                    self.retrieval_eval_service
                    .evaluate_case(
                        db=db,
                        knowledge_base_id=
                            knowledge_base_id,
                        eval_case=
                            eval_case,
                        top_k=
                            top_k,
                    )
                )

                eval_result = EvalResult(
                    experiment_id=
                        experiment.id,
                    eval_case_id=
                        eval_case.id,
                    retrieved_document_ids=
                        result_data[
                            "retrieved_document_ids"
                        ],
                    retrieved_chunk_ids=
                        result_data[
                            "retrieved_chunk_ids"
                        ],
                    retrieved_distances=
                        result_data[
                            "retrieved_distances"
                        ],
                    retrieval_context=
                        result_data[
                            "retrieval_context"
                        ],
                    expected_rank=
                        result_data[
                            "expected_rank"
                        ],
                    hit_at_k=
                        result_data[
                            "hit_at_k"
                        ],
                    reciprocal_rank=
                        result_data[
                            "reciprocal_rank"
                        ],
                    actual_answer=
                        None,
                    correctness_score=
                        None,
                    faithfulness_score=
                        None,
                    relevancy_score=
                        None,
                    refusal_score=
                        None,
                    passed=
                        result_data[
                            "hit_at_k"
                        ],
                    metrics={},
                    judge_metadata={},
                )

                self.result_repository.create(
                    db=db,
                    entity=eval_result,
                )

                case_results.append(
                    result_data
                )

            aggregate = (
                self.retrieval_eval_service
                .aggregate(
                    case_results
                )
            )

            experiment.hit_rate = (
                aggregate[
                    "hit_rate"
                ]
            )

            experiment.mrr = (
                aggregate[
                    "mrr"
                ]
            )

            experiment.metrics = (
                aggregate
            )

            experiment.status = (
                "completed"
            )

            db.commit()

            db.refresh(
                experiment
            )

            return experiment

        except Exception:
            db.rollback()

            experiment = (
                self.experiment_repository
                .get(
                    db=db,
                    entity_id=
                        experiment.id,
                )
            )

            if experiment is not None:
                experiment.status = (
                    "failed"
                )

                db.commit()

            raise

    def get(
        self,
        db: Session,
        experiment_id: UUID,
    ) -> EvalExperiment | None:
        return (
            self.experiment_repository
            .get(
                db=db,
                entity_id=
                    experiment_id,
            )
        )

    def list_by_dataset_id(
        self,
        db: Session,
        dataset_id: UUID,
    ) -> list[EvalExperiment]:
        return (
            self.experiment_repository
            .list_by_dataset_id(
                db=db,
                dataset_id=
                    dataset_id,
            )
        )