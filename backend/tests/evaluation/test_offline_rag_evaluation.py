import json
import os
from pathlib import Path
from statistics import mean
from types import SimpleNamespace

import pytest
import yaml

from deepeval.metrics import (
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
    FaithfulnessMetric,
)
from deepeval.test_case import LLMTestCase

from app.core.config import settings
from app.services.retrieval_eval_service import (
    RetrievalEvalService,
)


EVALUATION_DIR = Path(
    __file__
).resolve().parent

CONFIG_PATH = (
    EVALUATION_DIR
    / "config"
    / "offline_rag.yaml"
)

DATASET_PATH = (
    EVALUATION_DIR
    / "datasets"
    / "offline_rag_goldens.json"
)


def configure_judge():
    if not settings.LLM_API_KEY:
        raise RuntimeError(
            "LLM_API_KEY is not configured."
        )

    os.environ.setdefault(
        "OPENAI_API_KEY",
        settings.LLM_API_KEY,
    )


def load_config():
    with CONFIG_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return yaml.safe_load(file)


def load_dataset():
    with DATASET_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def build_eval_case(case):
    """
    RetrievalEvalService only requires these
    EvalCase attributes for deterministic
    retrieval evaluation.

    We intentionally avoid database records
    because this is a controlled offline lab.
    """

    return SimpleNamespace(
        question=case["input"],
        expected_document_id=None,
        expected_chunk_id=None,
        expected_sources=case[
            "expected_sources"
        ],
        expected_text=None,
    )


def build_retrieval_context(case):
    return [
        {
            "rank": rank,
            "document_external_id":
                item["source"],
            "text":
                item["text"],
        }
        for rank, item
        in enumerate(
            case["retrieved"],
            start=1,
        )
    ]


def build_deepeval_metrics(config):
    metric_config = config["metrics"]

    model = config[
        "judge"
    ]["model"]

    verbose = config[
        "judge"
    ].get(
        "verbose",
        False,
    )

    return {
        "contextual_precision":
            ContextualPrecisionMetric(
                threshold=metric_config[
                    "contextual_precision"
                ]["threshold"],
                model=model,
                include_reason=True,
                strict_mode=False,
                verbose_mode=verbose,
            ),

        "contextual_recall":
            ContextualRecallMetric(
                threshold=metric_config[
                    "contextual_recall"
                ]["threshold"],
                model=model,
                include_reason=True,
                strict_mode=False,
                verbose_mode=verbose,
            ),

        "contextual_relevancy":
            ContextualRelevancyMetric(
                threshold=metric_config[
                    "contextual_relevancy"
                ]["threshold"],
                model=model,
                include_reason=True,
                strict_mode=False,
                verbose_mode=verbose,
            ),

        "faithfulness":
            FaithfulnessMetric(
                threshold=metric_config[
                    "faithfulness"
                ]["threshold"],
                model=model,
                include_reason=True,
                strict_mode=False,
                verbose_mode=verbose,
            ),

        "answer_relevancy":
            AnswerRelevancyMetric(
                threshold=metric_config[
                    "answer_relevancy"
                ]["threshold"],
                model=model,
                include_reason=True,
                strict_mode=False,
                verbose_mode=verbose,
            ),
    }


def score_deepeval_case(
    case,
    config,
):
    retrieval_context = [
        item["text"]
        for item in case["retrieved"]
    ]

    test_case = LLMTestCase(
        input=case["input"],
        actual_output=case[
            "actual_output"
        ],
        expected_output=case[
            "expected_output"
        ],
        retrieval_context=
            retrieval_context,
    )

    metrics = build_deepeval_metrics(
        config
    )

    results = {}

    for name, metric in metrics.items():
        metric.measure(
            test_case
        )

        results[name] = {
            "score": metric.score,
            "reason": metric.reason,
            "passed":
                metric.is_successful(),
        }

    return results


def score_ir_case(
    case,
    top_k,
    retrieval_service,
):
    retrieval_context = (
        build_retrieval_context(
            case
        )
    )

    retrieved_sources = [
        item["source"]
        for item in case["retrieved"]
    ]

    eval_case = build_eval_case(
        case
    )

    return (
        retrieval_service
        .evaluate_retrieved_case(
            eval_case=eval_case,
            top_k=top_k,

            retrieved_document_ids=[],

            retrieved_document_external_ids=
                retrieved_sources,

            retrieved_chunk_ids=[],

            retrieved_distances=[],

            retrieval_context=
                retrieval_context,
        )
    )


def format_score(value):
    if value is None:
        return "N/A"

    return f"{value:.3f}"


def print_case_report(
    case_id,
    ir,
    semantic,
):
    print()
    print("=" * 72)
    print(
        f"CASE: {case_id}"
    )
    print("=" * 72)

    print()
    print("CLASSICAL RETRIEVAL")
    print("-" * 72)

    print(
        "Hit@K                 ",
        "1.000"
        if ir["hit_at_k"]
        else "0.000",
    )

    print(
        "Precision@K           ",
        format_score(
            ir["precision_at_k"]
        ),
    )

    print(
        "Recall@K              ",
        format_score(
            ir["recall_at_k"]
        ),
    )

    print(
        "Reciprocal Rank       ",
        format_score(
            ir["reciprocal_rank"]
        ),
    )

    print()
    print("DEEPEVAL RETRIEVAL")
    print("-" * 72)

    for metric_name in [
        "contextual_precision",
        "contextual_recall",
        "contextual_relevancy",
    ]:
        result = semantic[
            metric_name
        ]

        print(
            f"{metric_name:24}",
            format_score(
                result["score"]
            ),
        )

    print()
    print("DEEPEVAL GENERATION")
    print("-" * 72)

    for metric_name in [
        "faithfulness",
        "answer_relevancy",
    ]:
        result = semantic[
            metric_name
        ]

        print(
            f"{metric_name:24}",
            format_score(
                result["score"]
            ),
        )


def print_suite_report(
    ir_summary,
    semantic_results,
):
    print()
    print()
    print("#" * 72)
    print("OFFLINE RAG EVALUATION SUMMARY")
    print("#" * 72)

    print()
    print("CLASSICAL RETRIEVAL")
    print("-" * 72)

    print(
        "Hit Rate@K            ",
        format_score(
            ir_summary[
                "hit_rate"
            ]
        ),
    )

    print(
        "Mean Precision@K      ",
        format_score(
            ir_summary[
                "precision_at_k"
            ]
        ),
    )

    print(
        "Mean Recall@K         ",
        format_score(
            ir_summary[
                "recall_at_k"
            ]
        ),
    )

    print(
        "MRR                   ",
        format_score(
            ir_summary[
                "mrr"
            ]
        ),
    )

    print()
    print("DEEPEVAL")
    print("-" * 72)

    metric_names = [
        "contextual_precision",
        "contextual_recall",
        "contextual_relevancy",
        "faithfulness",
        "answer_relevancy",
    ]

    for metric_name in metric_names:
        scores = [
            result[
                metric_name
            ]["score"]
            for result
            in semantic_results
            if (
                result[
                    metric_name
                ]["score"]
                is not None
            )
        ]

        average = (
            mean(scores)
            if scores
            else None
        )

        print(
            f"Mean {metric_name:19}",
            format_score(
                average
            ),
        )


def test_generic_offline_rag_evaluation():
    """
    One-pass offline RAG evaluation lab.

    This is intentionally NOT a quality gate.

    The dataset contains good and bad cases
    so that we can observe how individual
    metrics respond to different failure
    modes.
    """

    configure_judge()

    config = load_config()
    dataset = load_dataset()

    top_k = config[
        "retrieval"
    ]["top_k"]

    retrieval_service = (
        RetrievalEvalService()
    )

    ir_results = []
    semantic_results = []

    for case in dataset["cases"]:
        ir = score_ir_case(
            case=case,
            top_k=top_k,
            retrieval_service=
                retrieval_service,
        )

        semantic = (
            score_deepeval_case(
                case=case,
                config=config,
            )
        )

        ir_results.append(
            ir
        )

        semantic_results.append(
            semantic
        )

        print_case_report(
            case_id=case["id"],
            ir=ir,
            semantic=semantic,
        )

        #
        # We assert that evaluation executed,
        # NOT that every deliberately bad
        # test case passed its threshold.
        #
        assert (
            ir["precision_at_k"]
            is not None
        )

        assert (
            ir["recall_at_k"]
            is not None
        )

        assert (
            ir["reciprocal_rank"]
            is not None
        )

        for result in (
            semantic.values()
        ):
            assert (
                result["score"]
                is not None
            )

            assert (
                0.0
                <= result["score"]
                <= 1.0
            )

    ir_summary = (
        retrieval_service.aggregate(
            ir_results
        )
    )

    print_suite_report(
        ir_summary=
            ir_summary,
        semantic_results=
            semantic_results,
    )