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
from app.services.evaluators import (
    EvaluationInput,
    EvaluationMetricResult,
    EvaluatorRegistry,
)
from app.services.generation_eval_service import (
    GenerationEvalService,
)
from app.services.retrieval_eval_service import (
    RetrievalEvalService,
)


class EvalExperimentService:

    def __init__(
        self,
    ):
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

        self.evaluator_registry = (
            EvaluatorRegistry()
        )

    def _validate_dataset(
        self,
        db: Session,
        dataset_id: UUID,
        knowledge_base_id: UUID,
    ) -> tuple[
        EvalDataset,
        KnowledgeBase,
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
            knowledge_base,
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

    def _metric_to_dict(
        self,
        result:
            EvaluationMetricResult,
    ) -> dict:
        """
        Normalize evaluator output for
        EvalResult.metrics JSON.

        This product-level representation
        keeps Knowgentiq independent from
        the underlying evaluation engine.
        """

        return {
            "score":
                result.score,

            "passed":
                result.passed,

            "threshold":
                result.threshold,

            "reason":
                result.reason,

            "evaluator_type":
                result.evaluator_type,

            "evaluator_engine":
                result.evaluator_engine,

            "metadata":
                result.metadata,
        }

    def _aggregate_metric(
        self,
        results: list[
            EvaluationMetricResult
        ],
    ) -> dict:
        """
        Aggregate one evaluator metric.

        Results with score=None are excluded
        from the metric denominator.

        Examples:

        - correctness is normally unscored
          for unanswerable cases.

        - refusal correctness is normally
          unscored for answerable cases.
        """

        scored = [
            result
            for result
            in results
            if result.score is not None
        ]

        scored_case_count = len(
            scored
        )

        unscored_case_count = (
            len(
                results
            )
            - scored_case_count
        )

        if scored_case_count == 0:
            return {
                "scored_case_count":
                    0,

                "unscored_case_count":
                    unscored_case_count,

                "passed_count":
                    0,

                "failed_count":
                    0,

                "average_score":
                    None,

                "pass_rate":
                    None,
            }

        passed_count = sum(
            1
            for result
            in scored
            if result.passed is True
        )

        failed_count = (
            scored_case_count
            - passed_count
        )

        average_score = (
            sum(
                float(
                    result.score
                    or 0.0
                )
                for result
                in scored
            )
            / scored_case_count
        )

        pass_rate = (
            passed_count
            / scored_case_count
        )

        return {
            "scored_case_count":
                scored_case_count,

            "unscored_case_count":
                unscored_case_count,

            "passed_count":
                passed_count,

            "failed_count":
                failed_count,

            "average_score":
                round(
                    average_score,
                    4,
                ),

            "pass_rate":
                round(
                    pass_rate,
                    4,
                ),
        }

    def _accumulate_judge_usage(
        self,
        result:
            EvaluationMetricResult,
        totals: dict,
    ) -> None:
        """
        Add evaluator LLM usage and latency
        into run-level totals.
        """

        metadata = (
            result.metadata
            or {}
        )

        usage = (
            metadata.get(
                "usage"
            )
            or {}
        )

        totals[
            "prompt_tokens"
        ] += int(
            usage.get(
                "prompt_tokens",
                0,
            )
            or 0
        )

        totals[
            "completion_tokens"
        ] += int(
            usage.get(
                "completion_tokens",
                0,
            )
            or 0
        )

        totals[
            "total_tokens"
        ] += int(
            usage.get(
                "total_tokens",
                0,
            )
            or 0
        )

        totals[
            "latency_ms"
        ] += float(
            metadata.get(
                "latency_ms",
                0.0,
            )
            or 0.0
        )

        if usage:
            totals[
                "judge_calls"
            ] += 1

    def _determine_case_passed(
        self,
        retrieval_data: dict,
        answerable: bool,
        faithfulness_result:
            EvaluationMetricResult,
        relevancy_result:
            EvaluationMetricResult,
        correctness_result:
            EvaluationMetricResult,
        refusal_result:
            EvaluationMetricResult,
        run_judges: bool,
    ) -> bool | None:
        """
        Determine the generation/RAG answer
        pass state for one evaluation case.

        IMPORTANT:

        Retrieval quality and generation
        quality are separate dimensions.

        A retrieval Hit@K miss does NOT
        automatically make a generated answer
        fail when judge metrics demonstrate
        that the answer is good.

        This is necessary because:

        - multiple sources may support the
          same answer;

        - a golden dataset may identify one
          preferred source while another
          retrieved source is still valid;

        - Hit@K measures retrieval against
          configured ground truth, not answer
          correctness.

        When judges are enabled:

        Answerable cases require:
        - faithfulness
        - answer relevancy
        - correctness

        Unanswerable cases require:
        - faithfulness
        - answer relevancy
        - refusal correctness

        When judges are disabled:

        Retrieval Hit@K is used as the only
        available deterministic case outcome
        when retrieval ground truth exists.

        Otherwise the case remains unscored.
        """

        has_retrieval_ground_truth = (
            retrieval_data.get(
                "has_retrieval_ground_truth",
                False,
            )
        )

        if not run_judges:
            if has_retrieval_ground_truth:
                return (
                    retrieval_data.get(
                        "hit_at_k"
                    )
                    is True
                )

            return None

        required_results = [
            faithfulness_result.passed,
            relevancy_result.passed,
        ]

        if answerable:
            required_results.append(
                correctness_result.passed
            )

        else:
            required_results.append(
                refusal_result.passed
            )

        #
        # None means the required judge metric
        # could not produce a result.
        #
        if any(
            result is None
            for result
            in required_results
        ):
            return None

        return all(
            result is True
            for result
            in required_results
        )

    def run_retrieval_experiment(
        self,
        db: Session,
        dataset_id: UUID,
        knowledge_base_id: UUID,
        name: str,
        top_k: int,
    ) -> EvalExperiment:
        """
        Run retrieval-only evaluation.

        Metrics:

        - Hit@K
        - Precision@K
        - Recall@K
        - Reciprocal Rank
        - Mean Reciprocal Rank
        """

        if top_k < 1:
            raise ValueError(
                "top_k must be greater than 0."
            )

        (
            dataset,
            knowledge_base,
            cases,
        ) = self._validate_dataset(
            db=db,

            dataset_id=
                dataset_id,

            knowledge_base_id=
                knowledge_base_id,
        )

        experiment = EvalExperiment(
            dataset_id=
                dataset.id,

            knowledge_base_id=
                knowledge_base.id,

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

                        "retrieved_document_external_ids":
                            result_data[
                                "retrieved_document_external_ids"
                            ],
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

            #
            # Retrieval-only experiment keeps
            # a consistent top-level structure
            # with full RAG experiments.
            #
            experiment.metrics = {
                "retrieval":
                    aggregate,

                "cases": {
                    "case_count":
                        len(
                            cases
                        ),

                    "scored_case_count":
                        aggregate[
                            "scored_case_count"
                        ],

                    "unscored_case_count":
                        aggregate[
                            "unscored_case_count"
                        ],
                },
            }

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
        evaluator_llm_configuration_id:
            UUID | None = None,
        run_judges: bool = True,
    ) -> EvalExperiment:
        """
        Execute a full Knowgentiq RAG
        evaluation run.

        Retrieval:

        - Hit@K
        - Precision@K
        - Recall@K
        - Reciprocal Rank
        - MRR

        Generation:

        - Faithfulness
        - Answer relevancy
        - Correctness
        - Refusal correctness

        Performance:

        - Retrieval latency
        - Generation latency
        - Total RAG latency
        - Generation tokens
        - Judge tokens
        - Total evaluation tokens
        """

        if top_k < 1:
            raise ValueError(
                "top_k must be greater than 0."
            )

        (
            dataset,
            knowledge_base,
            cases,
        ) = self._validate_dataset(
            db=db,

            dataset_id=
                dataset_id,

            knowledge_base_id=
                knowledge_base_id,
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

        generation_metric_results = {
            "faithfulness":
                [],

            "answer_relevancy":
                [],

            "correctness":
                [],

            "refusal_correctness":
                [],
        }

        generation_usage = {
            "prompt_tokens":
                0,

            "completion_tokens":
                0,

            "total_tokens":
                0,
        }

        judge_usage = {
            "prompt_tokens":
                0,

            "completion_tokens":
                0,

            "total_tokens":
                0,

            "latency_ms":
                0.0,

            "judge_calls":
                0,
        }

        total_retrieval_ms = 0.0

        total_generation_ms = 0.0

        total_latency_ms = 0.0

        generator_llm_metadata = None

        evaluator_metadata = None

        completed_case_count = 0

        passed_case_count = 0

        failed_case_count = 0

        unscored_case_count = 0

        try:
            for eval_case in cases:

                #
                # 1. Execute the real RAG
                # pipeline.
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
                # 2. Score the exact retrieval
                # context used by generation.
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

                generator_llm_metadata = (
                    generation_data[
                        "llm"
                    ]
                )

                generation_usage[
                    "prompt_tokens"
                ] += int(
                    usage[
                        "prompt_tokens"
                    ]
                )

                generation_usage[
                    "completion_tokens"
                ] += int(
                    usage[
                        "completion_tokens"
                    ]
                )

                generation_usage[
                    "total_tokens"
                ] += int(
                    usage[
                        "total_tokens"
                    ]
                )

                total_retrieval_ms += float(
                    latency[
                        "retrieval_ms"
                    ]
                )

                total_generation_ms += float(
                    latency[
                        "generation_ms"
                    ]
                )

                total_latency_ms += float(
                    latency[
                        "total_ms"
                    ]
                )

                #
                # 3. Common generation
                # evaluation input.
                #
                evaluation_input = (
                    EvaluationInput(
                        question=
                            eval_case.question,

                        actual_answer=
                            generation_data[
                                "actual_answer"
                            ],

                        expected_answer=
                            eval_case
                            .expected_answer,

                        retrieved_context=[
                            item.get(
                                "text",
                                "",
                            )
                            for item
                            in generation_data[
                                "retrieval_context"
                            ]
                        ],

                        expected_context=(
                            [
                                eval_case
                                .expected_text
                            ]
                            if (
                                eval_case
                                .expected_text
                            )
                            else []
                        ),

                        metadata={
                            #
                            # Runtime judge
                            # dependencies.
                            #
                            "db":
                                db,

                            "tenant_id":
                                knowledge_base
                                .tenant_id,

                            "evaluator_llm_configuration_id":
                                evaluator_llm_configuration_id,

                            #
                            # Golden case
                            # metadata.
                            #
                            "answerable":
                                eval_case
                                .answerable,
                        },
                    )
                )

                #
                # 4. Generation-quality
                # evaluators.
                #
                if run_judges:
                    faithfulness_result = (
                        self.evaluator_registry
                        .get(
                            "faithfulness"
                        )
                        .evaluate(
                            evaluation_input
                        )
                    )

                    relevancy_result = (
                        self.evaluator_registry
                        .get(
                            "answer_relevancy"
                        )
                        .evaluate(
                            evaluation_input
                        )
                    )

                    correctness_result = (
                        self.evaluator_registry
                        .get(
                            "correctness"
                        )
                        .evaluate(
                            evaluation_input
                        )
                    )

                    refusal_result = (
                        self.evaluator_registry
                        .get(
                            "refusal_correctness"
                        )
                        .evaluate(
                            evaluation_input
                        )
                    )

                else:
                    faithfulness_result = (
                        EvaluationMetricResult(
                            metric_name=
                                "faithfulness",

                            score=
                                None,

                            passed=
                                None,

                            reason=(
                                "LLM judge evaluation "
                                "was disabled."
                            ),

                            evaluator_type=
                                "llm_judge",

                            evaluator_engine=
                                "knowgentiq",
                        )
                    )

                    relevancy_result = (
                        EvaluationMetricResult(
                            metric_name=
                                "answer_relevancy",

                            score=
                                None,

                            passed=
                                None,

                            reason=(
                                "LLM judge evaluation "
                                "was disabled."
                            ),

                            evaluator_type=
                                "llm_judge",

                            evaluator_engine=
                                "knowgentiq",
                        )
                    )

                    correctness_result = (
                        EvaluationMetricResult(
                            metric_name=
                                "correctness",

                            score=
                                None,

                            passed=
                                None,

                            reason=(
                                "LLM judge evaluation "
                                "was disabled."
                            ),

                            evaluator_type=
                                "llm_judge",

                            evaluator_engine=
                                "knowgentiq",
                        )
                    )

                    refusal_result = (
                        EvaluationMetricResult(
                            metric_name=
                                "refusal_correctness",

                            score=
                                None,

                            passed=
                                None,

                            reason=(
                                "LLM judge evaluation "
                                "was disabled."
                            ),

                            evaluator_type=
                                "llm_judge",

                            evaluator_engine=
                                "knowgentiq",
                        )
                    )

                generation_metric_results[
                    "faithfulness"
                ].append(
                    faithfulness_result
                )

                generation_metric_results[
                    "answer_relevancy"
                ].append(
                    relevancy_result
                )

                generation_metric_results[
                    "correctness"
                ].append(
                    correctness_result
                )

                generation_metric_results[
                    "refusal_correctness"
                ].append(
                    refusal_result
                )

                #
                # Capture evaluator profile
                # and judge usage.
                #
                for metric_result in (
                    faithfulness_result,
                    relevancy_result,
                    correctness_result,
                    refusal_result,
                ):
                    metric_evaluator = (
                        metric_result
                        .metadata
                        .get(
                            "evaluator"
                        )
                        if (
                            metric_result
                            .metadata
                        )
                        else None
                    )

                    if (
                        evaluator_metadata
                        is None
                        and metric_evaluator
                    ):
                        evaluator_metadata = (
                            metric_evaluator
                        )

                    self._accumulate_judge_usage(
                        metric_result,
                        judge_usage,
                    )

                #
                # 5. Complete per-case metric
                # bundle.
                #
                metrics = {
                    #
                    # Retrieval metrics:
                    #
                    # hit_at_k
                    # precision_at_k
                    # recall_at_k
                    # reciprocal_rank
                    #
                    **retrieval_data[
                        "metrics"
                    ],

                    #
                    # Generation.
                    #
                    "faithfulness":
                        self._metric_to_dict(
                            faithfulness_result
                        ),

                    "answer_relevancy":
                        self._metric_to_dict(
                            relevancy_result
                        ),

                    "correctness":
                        self._metric_to_dict(
                            correctness_result
                        ),

                    "refusal_correctness":
                        self._metric_to_dict(
                            refusal_result
                        ),

                    #
                    # Performance.
                    #
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
                # 6. Determine generation/RAG
                # answer pass state.
                #
                # Retrieval is intentionally
                # evaluated separately.
                #
                case_passed = (
                    self._determine_case_passed(
                        retrieval_data=
                            retrieval_data,

                        answerable=
                            eval_case
                            .answerable,

                        faithfulness_result=
                            faithfulness_result,

                        relevancy_result=
                            relevancy_result,

                        correctness_result=
                            correctness_result,

                        refusal_result=
                            refusal_result,

                        run_judges=
                            run_judges,
                    )
                )

                if case_passed is True:
                    passed_case_count += 1

                elif case_passed is False:
                    failed_case_count += 1

                else:
                    unscored_case_count += 1

                completed_case_count += 1

                #
                # 7. Persist case result.
                #
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
                        correctness_result
                        .score,

                    faithfulness_score=
                        faithfulness_result
                        .score,

                    relevancy_score=
                        relevancy_result
                        .score,

                    refusal_score=
                        refusal_result
                        .score,

                    passed=
                        case_passed,

                    metrics=
                        metrics,

                    judge_metadata={
                        "generator":
                            generation_data[
                                "llm"
                            ],

                        "evaluator":
                            (
                                evaluator_metadata
                                if run_judges
                                else None
                            ),

                        "expected_answer":
                            eval_case
                            .expected_answer,

                        "answerable":
                            eval_case
                            .answerable,

                        "expected_sources":
                            eval_case
                            .expected_sources
                            or [],

                        "retrieved_document_external_ids":
                            generation_data[
                                "retrieved_document_external_ids"
                            ],

                        "generation_usage":
                            usage,

                        "generation_latency":
                            latency,

                        "run_judges":
                            run_judges,
                    },
                )

                self.result_repository.create(
                    db=db,

                    entity=
                        eval_result,
                )

            #
            # 8. Aggregate retrieval.
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

                average_generation_tokens = (
                    generation_usage[
                        "total_tokens"
                    ]
                    / case_count
                )

            else:
                average_retrieval_ms = (
                    0.0
                )

                average_generation_ms = (
                    0.0
                )

                average_total_ms = (
                    0.0
                )

                average_generation_tokens = (
                    0.0
                )

            if (
                judge_usage[
                    "judge_calls"
                ]
            ):
                average_judge_latency_ms = (
                    judge_usage[
                        "latency_ms"
                    ]
                    / judge_usage[
                        "judge_calls"
                    ]
                )

                average_judge_tokens = (
                    judge_usage[
                        "total_tokens"
                    ]
                    / judge_usage[
                        "judge_calls"
                    ]
                )

            else:
                average_judge_latency_ms = (
                    0.0
                )

                average_judge_tokens = (
                    0.0
                )

            #
            # 9. Aggregate generation.
            #
            generation_aggregate = {
                metric_name:
                    self._aggregate_metric(
                        metric_results
                    )

                for (
                    metric_name,
                    metric_results,
                ) in (
                    generation_metric_results
                    .items()
                )
            }

            total_evaluation_tokens = (
                generation_usage[
                    "total_tokens"
                ]
                + judge_usage[
                    "total_tokens"
                ]
            )

            #
            # 10. Overall generation-quality
            # pass rate.
            #
            scored_overall_cases = (
                passed_case_count
                + failed_case_count
            )

            if scored_overall_cases:
                overall_pass_rate = (
                    passed_case_count
                    / scored_overall_cases
                )

            else:
                overall_pass_rate = (
                    None
                )

            #
            # 11. Persist the complete
            # experiment metric hierarchy.
            #
            aggregate_metrics = {
                "retrieval":
                    retrieval_aggregate,

                "generation":
                    generation_aggregate,

                "cases": {
                    "case_count":
                        completed_case_count,

                    "passed_count":
                        passed_case_count,

                    "failed_count":
                        failed_case_count,

                    "unscored_count":
                        unscored_case_count,

                    "pass_rate":
                        (
                            round(
                                overall_pass_rate,
                                4,
                            )
                            if (
                                overall_pass_rate
                                is not None
                            )
                            else None
                        ),
                },

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

                    "total_rag_ms":
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

                    "average_rag_ms":
                        round(
                            average_total_ms,
                            2,
                        ),

                    "total_judge_ms":
                        round(
                            judge_usage[
                                "latency_ms"
                            ],
                            2,
                        ),

                    "average_judge_call_ms":
                        round(
                            average_judge_latency_ms,
                            2,
                        ),
                },

                "usage": {
                    "generation": {
                        "prompt_tokens":
                            generation_usage[
                                "prompt_tokens"
                            ],

                        "completion_tokens":
                            generation_usage[
                                "completion_tokens"
                            ],

                        "total_tokens":
                            generation_usage[
                                "total_tokens"
                            ],

                        "average_tokens_per_case":
                            round(
                                average_generation_tokens,
                                2,
                            ),
                    },

                    "judge": {
                        "judge_calls":
                            judge_usage[
                                "judge_calls"
                            ],

                        "prompt_tokens":
                            judge_usage[
                                "prompt_tokens"
                            ],

                        "completion_tokens":
                            judge_usage[
                                "completion_tokens"
                            ],

                        "total_tokens":
                            judge_usage[
                                "total_tokens"
                            ],

                        "average_tokens_per_call":
                            round(
                                average_judge_tokens,
                                2,
                            ),
                    },

                    "total_evaluation_tokens":
                        total_evaluation_tokens,
                },

                "generator":
                    generator_llm_metadata,

                "evaluator":
                    evaluator_metadata,

                "run_judges":
                    run_judges,
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

            if generator_llm_metadata:
                experiment.llm_model = (
                    generator_llm_metadata
                    .get(
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
    ) -> list[
        EvalExperiment
    ]:
        return (
            self.experiment_repository
            .list_by_dataset_id(
                db=db,

                dataset_id=
                    dataset_id,
            )
        )