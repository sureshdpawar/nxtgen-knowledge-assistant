from deepeval.metrics import (
    FaithfulnessMetric,
)
from deepeval.test_case import (
    LLMTestCase,
)


def build_metric():
    return FaithfulnessMetric(
        threshold=0.8,
        include_reason=True,
        verbose_mode=True,
        penalize_ambiguous_claims=True,
    )


def test_faithfulness_fully_grounded():
    test_case = LLMTestCase(
        input=(
            "What AI services does "
            "NXTGEN provide?"
        ),
        actual_output=(
            "NXTGEN provides machine learning, "
            "generative AI, and RAG solutions."
        ),
        retrieval_context=[
            (
                "NXTGEN provides machine learning, "
                "generative AI, and RAG solutions."
            ),
        ],
    )

    metric = build_metric()

    metric.measure(
        test_case
    )

    print(
        "\nFULLY GROUNDED SCORE:",
        metric.score,
    )

    print(
        "REASON:",
        metric.reason,
    )

    assert metric.score >= 0.8


def test_faithfulness_direct_contradiction():
    test_case = LLMTestCase(
        input=(
            "What AI services does "
            "NXTGEN provide?"
        ),
        actual_output=(
            "NXTGEN does not provide "
            "generative AI or RAG solutions."
        ),
        retrieval_context=[
            (
                "NXTGEN provides machine learning, "
                "generative AI, and RAG solutions."
            ),
        ],
    )

    metric = build_metric()

    metric.measure(
        test_case
    )

    print(
        "\nCONTRADICTION SCORE:",
        metric.score,
    )

    print(
        "REASON:",
        metric.reason,
    )

    assert metric.score < 0.8


def test_faithfulness_mixed_claims():
    test_case = LLMTestCase(
        input=(
            "Describe NXTGEN's services."
        ),
        actual_output=(
            "NXTGEN provides machine learning services. "
            "NXTGEN provides generative AI services. "
            "NXTGEN provides RAG solutions. "
            "NXTGEN does not provide cloud services. "
            "NXTGEN does not provide consulting services."
        ),
        retrieval_context=[
            (
                "NXTGEN provides machine learning services."
            ),
            (
                "NXTGEN provides generative AI services."
            ),
            (
                "NXTGEN provides RAG solutions."
            ),
            (
                "NXTGEN provides cloud services."
            ),
            (
                "NXTGEN provides consulting services."
            ),
        ],
    )

    metric = FaithfulnessMetric(
        threshold=0.8,
        include_reason=True,
        verbose_mode=True,
        penalize_ambiguous_claims=False,
    )

    metric.measure(
        test_case
    )

    print(
        "\nFAITHFULNESS SCORE:",
        metric.score,
    )

    print(
        "\nFAITHFULNESS REASON:",
        metric.reason,
    )

    print(
        "\nSUCCESS:",
        metric.is_successful(),
    )

    # Do NOT force an expected numeric score yet.
    assert 0.0 <= metric.score <= 1.0
    
    
    def test_faithfulness_partial_score():
        test_case = LLMTestCase(
        input=(
            "What services does "
            "NXTGEN provide?"
        ),
        actual_output=(
            "NXTGEN provides machine learning. "
            "NXTGEN provides generative AI. "
            "NXTGEN provides RAG solutions. "
            "NXTGEN does not provide cloud services. "
            "NXTGEN does not provide consulting services."
        ),
        retrieval_context=[
            (
                "NXTGEN provides machine learning. "
                "NXTGEN provides generative AI. "
                "NXTGEN provides RAG solutions. "
                "NXTGEN provides cloud services. "
                "NXTGEN provides consulting services."
            ),
        ],
    )

    metric = FaithfulnessMetric(
        threshold=0.8,
        include_reason=True,
        verbose_mode=True,
        penalize_ambiguous_claims=True,
    )

    metric.measure(
        test_case
    )

    print(
        "\nFAITHFULNESS SCORE:",
        metric.score,
    )

    print(
        "REASON:",
        metric.reason,
    )

    assert 0.0 < metric.score < 1.0