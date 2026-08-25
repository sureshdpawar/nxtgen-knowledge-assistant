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
from app.models.knowledge_base import (
    KnowledgeBase,
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
from app.services.generation_eval_service import (
    GenerationEvalService,
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

        self.generation_eval_service = (
            GenerationEvalService()
        )

    def _validate_dataset(
        self,
        db: Session,
        dataset_id: UUID,
        knowledge_base_id: UUID,
    ) -> tuple[
        EvalDataset,
        list,
    ]:
        dataset = db.get(
            EvalDataset,
            dataset_id,
        )

        if dataset is None:
            raise ValueError(
                "Eval dataset not found."
            )

        if (
            dataset.knowledge_base_id
            != knowledge_base_id
        ):
            raise ValueError(
                "Eval dataset does not belong "
                "to the supplied Knowledge Base."
            )

        knowledge_base = db.get(
            KnowledgeBase,
            knowledge_base_id,
        )

        if knowledge_base is None:
            raise ValueError(
                "Knowledge Base not found."
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

        return (
            dataset,
            cases,
        )

    def _mark_failed(
        self,
        db: Session,
        experiment_id: UUID,
        exc: Exception,
    ) -> None:
        db.rollback()

        experiment = (
            self.experiment_repository
            .get(
                db=db,
                entity_id=
                    experiment_id,
            )
        )

        if experiment is None:
            return

        experiment.status = (
            "failed"
        )

        experiment.metrics = {
            "error":
                str(
                    exc
                ),
        }

        db.commit()

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
                "top_k must be greater than 0."
            )

        dataset, cases = (
            self._validate_dataset(
                db=db,

                dataset_id=
                    dataset_id,

                knowledge_base_id=
                    knowledge_base_id,
            )
        )

        experiment = EvalExperiment(
            dataset_id=
                dataset.id,

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
                entity=
                    experiment,
            )
        )

        db.commit()

        db.refresh(
            experiment
        )

        experiment_id = (
            experiment.id
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
                        experiment_id,

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

                    metrics=
                        result_data[
                            "metrics"
                        ],

                    judge_metadata={
                        "expected_sources":
                            eval_case
                            .expected_sources
                            or [],
                    },
                )

                self.result_repository.create(
                    db=db,
                    entity=
                        eval_result,
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

        except Exception as exc:
            self._mark_failed(
                db=db,

                experiment_id=
                    experiment_id,

                exc=
                    exc,
            )

            raise

    def run_rag_experiment(
        self,
        db: Session,
        dataset_id: UUID,
        knowledge_base_id: UUID,
        name: str,
        top_k: int,
    ) -> EvalExperiment:
        """
        Execute a full RAG evaluation run.

        Captures:

        - retrieval output
        - portable source identity
        - Hit@K
        - Reciprocal Rank
        - MRR
        - actual generated answer
        - expected answer
        - retrieval latency
        - generation latency
        - total latency
        - token usage
        - LLM profile/model metadata

        LLM-as-a-Judge metrics are added later.
        """

        if top_k < 1:
            raise ValueError(
                "top_k must be greater than 0."
            )

        dataset, cases = (
            self._validate_dataset(
                db=db,

                dataset_id=
                    dataset_id,

                knowledge_base_id=
                    knowledge_base_id,
            )
        )

        experiment = EvalExperiment(
            dataset_id=
                dataset.id,

            knowledge_base_id=
                knowledge_base_id,

            name=
                name,

            eval_type=
                "rag",

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
                entity=
                    experiment,
            )
        )

        db.commit()

        db.refresh(
            experiment
        )

        experiment_id = (
            experiment.id
        )

        retrieval_results = []

        total_prompt_tokens = 0

        total_completion_tokens = 0

        total_tokens = 0

        total_retrieval_ms = 0.0

        total_generation_ms = 0.0

        total_latency_ms = 0.0

        llm_metadata = None

        try:
            for eval_case in cases:
                #
                # One complete RAG execution.
                #
                generation_data = (
                    self.generation_eval_service
                    .evaluate_case(
                        db=db,

                        knowledge_base_id=
                            knowledge_base_id,

                        question=
                            eval_case.question,

                        top_k=
                            top_k,
                    )
                )

                #
                # Score the exact retrieval
                # that was used for generation.
                #
                retrieval_data = (
                    self.retrieval_eval_service
                    .evaluate_retrieved_case(
                        eval_case=
                            eval_case,

                        top_k=
                            top_k,

                        retrieved_document_ids=
                            generation_data[
                                "retrieved_document_ids"
                            ],

                        retrieved_document_external_ids=
                            generation_data[
                                "retrieved_document_external_ids"
                            ],

                        retrieved_chunk_ids=
                            generation_data[
                                "retrieved_chunk_ids"
                            ],

                        retrieved_distances=
                            generation_data[
                                "retrieved_distances"
                            ],

                        retrieval_context=
                            generation_data[
                                "retrieval_context"
                            ],
                    )
                )

                retrieval_results.append(
                    retrieval_data
                )

                usage = (
                    generation_data[
                        "usage"
                    ]
                )

                latency = (
                    generation_data[
                        "latency"
                    ]
                )

                llm_metadata = (
                    generation_data[
                        "llm"
                    ]
                )

                total_prompt_tokens += (
                    usage[
                        "prompt_tokens"
                    ]
                )

                total_completion_tokens += (
                    usage[
                        "completion_tokens"
                    ]
                )

                total_tokens += (
                    usage[
                        "total_tokens"
                    ]
                )

                total_retrieval_ms += (
                    latency[
                        "retrieval_ms"
                    ]
                )

                total_generation_ms += (
                    latency[
                        "generation_ms"
                    ]
                )

                total_latency_ms += (
                    latency[
                        "total_ms"
                    ]
                )

                #
                # Per-case metric bundle.
                #
                metrics = {
                    **retrieval_data[
                        "metrics"
                    ],

                    "latency": {
                        "retrieval_ms":
                            latency[
                                "retrieval_ms"
                            ],

                        "generation_ms":
                            latency[
                                "generation_ms"
                            ],

                        "total_ms":
                            latency[
                                "total_ms"
                            ],

                        "evaluator_type":
                            "deterministic",

                        "evaluator_engine":
                            "knowgentiq",
                    },

                    "token_usage": {
                        "prompt_tokens":
                            usage[
                                "prompt_tokens"
                            ],

                        "completion_tokens":
                            usage[
                                "completion_tokens"
                            ],

                        "total_tokens":
                            usage[
                                "total_tokens"
                            ],

                        "estimated":
                            usage[
                                "estimated"
                            ],

                        "evaluator_type":
                            "deterministic",

                        "evaluator_engine":
                            "knowgentiq",
                    },
                }

                #
                # Until generation-quality
                # judges are added, overall
                # pass reflects retrieval
                # when retrieval ground truth
                # exists.
                #
                case_passed = (
                    retrieval_data[
                        "hit_at_k"
                    ]
                )

                eval_result = EvalResult(
                    experiment_id=
                        experiment_id,

                    eval_case_id=
                        eval_case.id,

                    retrieved_document_ids=
                        generation_data[
                            "retrieved_document_ids"
                        ],

                    retrieved_chunk_ids=
                        generation_data[
                            "retrieved_chunk_ids"
                        ],

                    retrieved_distances=
                        generation_data[
                            "retrieved_distances"
                        ],

                    retrieval_context=
                        generation_data[
                            "retrieval_context"
                        ],

                    expected_rank=
                        retrieval_data[
                            "expected_rank"
                        ],

                    hit_at_k=
                        retrieval_data[
                            "hit_at_k"
                        ],

                    reciprocal_rank=
                        retrieval_data[
                            "reciprocal_rank"
                        ],

                    actual_answer=
                        generation_data[
                            "actual_answer"
                        ],

                    correctness_score=
                        None,

                    faithfulness_score=
                        None,

                    relevancy_score=
                        None,

                    refusal_score=
                        None,

                    passed=
                        case_passed,

                    metrics=
                        metrics,

                    judge_metadata={
                        #
                        # Generation model.
                        #
                        "llm":
                            generation_data[
                                "llm"
                            ],

                        #
                        # Golden answer.
                        #
                        "expected_answer":
                            eval_case
                            .expected_answer,

                        #
                        # Whether the question
                        # should be answerable
                        # from the KB.
                        #
                        "answerable":
                            eval_case
                            .answerable,

                        #
                        # Portable retrieval
                        # ground truth.
                        #
                        "expected_sources":
                            eval_case
                            .expected_sources
                            or [],

                        #
                        # Retrieved portable
                        # source identities.
                        #
                        "retrieved_document_external_ids":
                            generation_data[
                                "retrieved_document_external_ids"
                            ],

                        #
                        # Execution metadata.
                        #
                        "usage":
                            usage,

                        "latency":
                            latency,
                    },
                )

                self.result_repository.create(
                    db=db,
                    entity=
                        eval_result,
                )

            #
            # Retrieval aggregate.
            #
            retrieval_aggregate = (
                self.retrieval_eval_service
                .aggregate(
                    retrieval_results
                )
            )

            case_count = len(
                cases
            )

            if case_count:
                average_retrieval_ms = (
                    total_retrieval_ms
                    / case_count
                )

                average_generation_ms = (
                    total_generation_ms
                    / case_count
                )

                average_total_ms = (
                    total_latency_ms
                    / case_count
                )

                average_tokens = (
                    total_tokens
                    / case_count
                )

            else:
                average_retrieval_ms = 0.0

                average_generation_ms = 0.0

                average_total_ms = 0.0

                average_tokens = 0.0

            aggregate_metrics = {
                "retrieval":
                    retrieval_aggregate,

                "latency": {
                    "total_retrieval_ms":
                        round(
                            total_retrieval_ms,
                            2,
                        ),

                    "total_generation_ms":
                        round(
                            total_generation_ms,
                            2,
                        ),

                    "total_ms":
                        round(
                            total_latency_ms,
                            2,
                        ),

                    "average_retrieval_ms":
                        round(
                            average_retrieval_ms,
                            2,
                        ),

                    "average_generation_ms":
                        round(
                            average_generation_ms,
                            2,
                        ),

                    "average_total_ms":
                        round(
                            average_total_ms,
                            2,
                        ),
                },

                "usage": {
                    "prompt_tokens":
                        total_prompt_tokens,

                    "completion_tokens":
                        total_completion_tokens,

                    "total_tokens":
                        total_tokens,

                    "average_tokens_per_case":
                        round(
                            average_tokens,
                            2,
                        ),
                },

                "llm":
                    llm_metadata,
            }

            experiment.hit_rate = (
                retrieval_aggregate[
                    "hit_rate"
                ]
            )

            experiment.mrr = (
                retrieval_aggregate[
                    "mrr"
                ]
            )

            if llm_metadata:
                experiment.llm_model = (
                    llm_metadata.get(
                        "model"
                    )
                )

            experiment.metrics = (
                aggregate_metrics
            )

            experiment.status = (
                "completed"
            )

            db.commit()

            db.refresh(
                experiment
            )

            return experiment

        except Exception as exc:
            self._mark_failed(
                db=db,

                experiment_id=
                    experiment_id,

                exc=
                    exc,
            )

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