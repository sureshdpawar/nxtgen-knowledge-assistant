from dotenv import load_dotenv

from deepeval import assert_test
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
)
from deepeval.test_case import LLMTestCase


load_dotenv()


def test_basic_rag_quality():
    """
    Verify DeepEval can evaluate a basic grounded
    RAG response and enforce metric thresholds.

    This test intentionally uses DeepEval directly
    before integrating it with Knowgentiq's
    evaluation control plane.
    """

    test_case = LLMTestCase(
        input=(
            "What is the company's password policy?"
        ),
        actual_output=(
            "Passwords must contain at least "
            "12 characters and users must enable "
            "multi-factor authentication."
        ),
        retrieval_context=[
            (
                "Corporate password policy: "
                "passwords must contain at least "
                "12 characters."
            ),
            (
                "Multi-factor authentication is "
                "mandatory for all employee accounts."
            ),
        ],
    )

    metrics = [
        FaithfulnessMetric(
            threshold=0.8,
        ),
        AnswerRelevancyMetric(
            threshold=0.8,
        ),
    ]

    assert_test(
        test_case,
        metrics,
    )