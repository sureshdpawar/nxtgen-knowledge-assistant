from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class EvalExpectedSource(
    BaseModel
):
    type: str = Field(
        min_length=1,
        max_length=50,
    )

    value: str = Field(
        min_length=1,
        max_length=2000,
    )


class EvalDatasetCreate(
    BaseModel
):
    knowledge_base_id: UUID

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    version: str = Field(
        default="v1",
        min_length=1,
        max_length=50,
    )

    description: (
        str | None
    ) = None


class EvalDatasetRead(
    BaseModel
):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    knowledge_base_id: UUID

    name: str

    version: str

    description: (
        str | None
    )


class EvalCaseCreate(
    BaseModel
):
    dataset_id: UUID

    question: str = Field(
        min_length=1,
    )

    expected_document_id: (
        UUID | None
    ) = None

    expected_chunk_id: (
        UUID | None
    ) = None

    expected_sources: list[
        EvalExpectedSource
    ] = Field(
        default_factory=list,
    )

    expected_text: (
        str | None
    ) = None

    expected_answer: (
        str | None
    ) = None

    answerable: bool = True


class EvalCaseRead(
    BaseModel
):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    dataset_id: UUID

    question: str

    expected_document_id: (
        UUID | None
    )

    expected_chunk_id: (
        UUID | None
    )

    expected_sources: list[
        EvalExpectedSource
    ]

    expected_text: (
        str | None
    )

    expected_answer: (
        str | None
    )

    answerable: bool


class EvalExperimentRun(
    BaseModel
):
    """
    Request for retrieval-only
    evaluation runs.
    """

    dataset_id: UUID

    knowledge_base_id: UUID

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    top_k: int = Field(
        ge=1,
        le=100,
    )


class EvalRAGExperimentRun(
    EvalExperimentRun
):
    """
    Request for full RAG evaluation.

    evaluator_llm_configuration_id:

    - supplied:
        use that tenant LLM profile
        as the evaluator/judge

    - null:
        use tenant default LLM profile

    run_judges:

    - true:
        run generation-quality metrics

    - false:
        run RAG without LLM judges
    """

    evaluator_llm_configuration_id: (
        UUID | None
    ) = None

    run_judges: bool = True


class EvalExperimentRead(
    BaseModel
):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    dataset_id: UUID

    knowledge_base_id: UUID

    name: str

    eval_type: str

    top_k: int

    chunk_size: (
        int | None
    )

    chunk_overlap: (
        int | None
    )

    embedding_model: (
        str | None
    )

    llm_model: (
        str | None
    )

    status: str

    hit_rate: (
        float | None
    )

    mrr: (
        float | None
    )

    metrics: dict


class EvalResultRead(
    BaseModel
):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    experiment_id: UUID

    eval_case_id: UUID

    retrieved_document_ids: list

    retrieved_chunk_ids: list

    retrieved_distances: list

    retrieval_context: list

    expected_rank: (
        int | None
    )

    hit_at_k: (
        bool | None
    )

    reciprocal_rank: (
        float | None
    )

    actual_answer: (
        str | None
    )

    correctness_score: (
        float | None
    )

    faithfulness_score: (
        float | None
    )

    relevancy_score: (
        float | None
    )

    refusal_score: (
        float | None
    )

    passed: (
        bool | None
    )

    metrics: dict

    judge_metadata: dict


class EvalDatasetImportCase(
    BaseModel
):
    question: str = Field(
        min_length=1,
    )

    expected_answer: (
        str | None
    ) = None

    expected_text: (
        str | None
    ) = None

    expected_document_id: (
        UUID | None
    ) = None

    expected_chunk_id: (
        UUID | None
    ) = None

    expected_sources: list[
        EvalExpectedSource
    ] = Field(
        default_factory=list,
    )

    answerable: bool = True

    category: (
        str | None
    ) = None

    tags: list[str] = Field(
        default_factory=list,
    )


class EvalDatasetImportPayload(
    BaseModel
):
    knowledge_base_id: UUID

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    version: str = Field(
        default="v1",
        min_length=1,
        max_length=50,
    )

    description: (
        str | None
    ) = None

    cases: list[
        EvalDatasetImportCase
    ] = Field(
        min_length=1,
    )


class EvalDatasetImportRead(
    BaseModel
):
    dataset: EvalDatasetRead

    case_count: int


#
# Evaluation comparison
#


class EvalComparisonRequest(
    BaseModel
):
    baseline_experiment_id: UUID

    candidate_experiment_id: UUID


class EvalComparisonMetricRead(
    BaseModel
):
    metric: str

    baseline: (
        float
        | int
        | None
    )

    candidate: (
        float
        | int
        | None
    )

    delta: (
        float | None
    )

    higher_is_better: bool

    outcome: str


class EvalComparisonRunRead(
    BaseModel
):
    id: UUID

    name: str

    dataset_id: UUID

    knowledge_base_id: UUID

    eval_type: str

    status: str

    top_k: int

    embedding_model: (
        str | None
    )

    llm_model: (
        str | None
    )

    hit_rate: (
        float | None
    )

    mrr: (
        float | None
    )

    faithfulness: (
        float | None
    )

    answer_relevancy: (
        float | None
    )

    correctness: (
        float | None
    )

    refusal_correctness: (
        float | None
    )

    pass_rate: (
        float | None
    )

    average_rag_ms: (
        float | None
    )

    generation_tokens: (
        int | None
    )

    judge_tokens: (
        int | None
    )

    total_evaluation_tokens: (
        int | None
    )

    generator: (
        dict | None
    )

    evaluator: (
        dict | None
    )


class EvalComparisonCaseRunRead(
    BaseModel
):
    eval_case_id: UUID

    question: (
        str | None
    )

    answerable: (
        bool | None
    )

    passed: (
        bool | None
    )

    hit_at_k: (
        bool | None
    )

    expected_rank: (
        int | None
    )

    reciprocal_rank: (
        float | None
    )

    faithfulness: (
        float | None
    )

    answer_relevancy: (
        float | None
    )

    correctness: (
        float | None
    )

    refusal_correctness: (
        float | None
    )

    quality_score: (
        float | None
    )

    actual_answer: (
        str | None
    )


class EvalComparisonCaseRead(
    BaseModel
):
    eval_case_id: UUID

    question: (
        str | None
    )

    answerable: (
        bool | None
    )

    outcome: str

    quality_delta: (
        float | None
    )

    baseline:EvalComparisonCaseRunRead

    candidate:EvalComparisonCaseRunRead


class EvalComparisonSummaryRead(
    BaseModel
):
    improved_metric_count: int

    regressed_metric_count: int

    unchanged_metric_count: int

    improved_case_count: int

    regressed_case_count: int

    unchanged_case_count: int

    compared_case_count: int


class EvalComparisonRead(
    BaseModel
):
    baseline:EvalComparisonRunRead

    candidate:EvalComparisonRunRead

    summary:EvalComparisonSummaryRead

    metrics: list[
        EvalComparisonMetricRead
    ]

    improved_cases: list[
        EvalComparisonCaseRead
    ]

    regressed_cases: list[
        EvalComparisonCaseRead
    ]

    unchanged_cases: list[
        EvalComparisonCaseRead
    ]