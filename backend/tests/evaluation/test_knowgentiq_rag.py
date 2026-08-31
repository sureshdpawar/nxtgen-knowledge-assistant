import os
from pathlib import Path
from uuid import UUID

import pytest

from deepeval import assert_test
from deepeval.metrics import (
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
    FaithfulnessMetric,
)
from deepeval.test_case import LLMTestCase

from app.core.config import settings
from app.db.session import SessionLocal
from app.evaluation.config import (
    EvaluationRunConfig,
    load_evaluation_config,
)
from app.evaluation.dataset import (
    EvaluationCaseDefinition,
    EvaluationDatasetDefinition,
    load_evaluation_dataset,
)
from app.services.generation_eval_service import (
    GenerationEvalService,
)


EVALUATION_DIR = (
    Path(__file__).resolve().parent
)

CONFIG_PATH = (
    EVALUATION_DIR
    / "config"
    / "rag_ci.yaml"
)

DATASET_PATH = (
    EVALUATION_DIR
    / "datasets"
    / "rag_ci.json"
)


def _configure_deepeval_judge() -> None:
    """
    Temporary bridge between Knowgentiq's
    platform-level LLM secret and DeepEval's
    native OpenAI judge.

    Evaluation-specific secrets do not belong
    in .env.

    Product evaluation can later replace this
    with a tenant-aware DeepEvalBaseLLM adapter.
    """

    if not settings.LLM_API_KEY:
        raise RuntimeError(
            "Knowgentiq platform LLM_API_KEY "
            "is not configured."
        )

    os.environ.setdefault(
        "OPENAI_API_KEY",
        settings.LLM_API_KEY,
    )


def _load_test_definition() -> tuple[
    EvaluationRunConfig,
    EvaluationDatasetDefinition,
]:
    """
    Load CI evaluation configuration and the
    portable golden dataset.
    """

    run_config = (
        load_evaluation_config(
            CONFIG_PATH
        )
    )

    dataset = (
        load_evaluation_dataset(
            DATASET_PATH
        )
    )

    return (
        run_config,
        dataset,
    )


def _build_metrics(
    config: EvaluationRunConfig,
) -> list:
    """
    Convert configured metric definitions
    into native DeepEval metrics.

    Keep this mapping close to the CI suite
    until a reusable application boundary
    genuinely emerges.
    """

    enabled_metrics = (
        config.enabled_metrics()
    )

    metric_classes = {
        "faithfulness":
            FaithfulnessMetric,

        "answer_relevancy":
            AnswerRelevancyMetric,

        "contextual_precision":
            ContextualPrecisionMetric,

        "contextual_recall":
            ContextualRecallMetric,

        "contextual_relevancy":
            ContextualRelevancyMetric,
    }

    unsupported_metrics = (
        set(enabled_metrics)
        - set(metric_classes)
    )

    if unsupported_metrics:
        raise ValueError(
            "Unsupported DeepEval metrics: "
            + ", ".join(
                sorted(
                    unsupported_metrics
                )
            )
        )

    metrics = []

    for (
        metric_name,
        metric_config,
    ) in enabled_metrics.items():
        metric_class = (
            metric_classes[
                metric_name
            ]
        )

        metrics.append(
            metric_class(
                threshold=
                    metric_config.threshold,
            )
        )

    return metrics


def _get_knowledge_base_id(
    config: EvaluationRunConfig,
) -> UUID:
    """
    Resolve and validate the Knowledge Base
    targeted by this evaluation run.
    """

    try:
        return UUID(
            config
            .target
            .knowledge_base_id
        )

    except ValueError as exc:
        raise ValueError(
            "target.knowledge_base_id in "
            "rag_ci.yaml must be a valid UUID."
        ) from exc


def _extract_retrieval_context(
    generation_data: dict,
) -> list[str]:
    """
    Extract ranked textual retrieval context.

    Order must be preserved because contextual
    precision evaluates retrieval ranking.
    """

    return [
        text
        for text
        in (
            (
                item.get(
                    "text"
                )
                or ""
            ).strip()

            for item
            in generation_data.get(
                "retrieval_context",
                [],
            )
        )
        if text
    ]


RUN_CONFIG, DATASET = (
    _load_test_definition()
)

KNOWLEDGE_BASE_ID = (
    _get_knowledge_base_id(
        RUN_CONFIG
    )
)


@pytest.mark.parametrize(
    "case",
    DATASET.cases,
    ids=lambda case: case.id,
)
def test_real_knowgentiq_rag_quality(
    case: EvaluationCaseDefinition,
):
    """
    Execute one golden evaluation case through
    the real Knowgentiq RAG pipeline.

    One golden dataset case intentionally maps
    to one pytest/DeepEval test case so CI and
    Confident AI can report individual failures.

    CI does not persist EvalExperiment or
    EvalResult records.
    """

    _configure_deepeval_judge()

    metrics = (
        _build_metrics(
            RUN_CONFIG
        )
    )

    generation_service = (
        GenerationEvalService()
    )

    db = SessionLocal()

    try:
        generation_data = (
            generation_service
            .evaluate_case(
                db=db,

                knowledge_base_id=
                    KNOWLEDGE_BASE_ID,

                question=
                    case.question,

                top_k=
                    RUN_CONFIG
                    .retrieval
                    .top_k,
            )
        )

        actual_answer = (
            generation_data.get(
                "actual_answer"
            )
            or ""
        ).strip()

        retrieval_context = (
            _extract_retrieval_context(
                generation_data
            )
        )

        assert actual_answer, (
            f"Evaluation case "
            f"'{case.id}' returned "
            "an empty answer."
        )

        assert retrieval_context, (
            f"Evaluation case "
            f"'{case.id}' returned "
            "no retrieval context."
        )

        test_case = (
            LLMTestCase(
                input=
                    case.question,

                actual_output=
                    actual_answer,

                expected_output=
                    case.expected_answer,

                retrieval_context=
                    retrieval_context,
            )
        )

        assert_test(
            test_case=
                test_case,

            metrics=
                metrics,
        )

    finally:
        db.close()