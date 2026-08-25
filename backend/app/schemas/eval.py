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

    description: str | None = None


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

    description: str | None


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