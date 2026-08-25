from uuid import UUID

from sqlalchemy.orm import Session

from app.services.evaluators.base import (
    BaseEvaluator,
    EvaluationInput,
    EvaluationMetricResult,
)
from app.services.llm_judge_service import (
    LLMJudgeService,
)


class BaseLLMJudgeEvaluator(
    BaseEvaluator
):
    """
    Shared base class for Knowgentiq
    LLM-as-a-Judge evaluators.

    Runtime-only dependencies such as the
    DB session and tenant ID are supplied
    through EvaluationInput.metadata.

    These values are never persisted as
    metric metadata.
    """

    evaluator_type = (
        "llm_judge"
    )

    evaluator_engine = (
        "knowgentiq"
    )

    threshold: float = 0.8

    rubric: str = ""

    def __init__(self):
        self.judge_service = (
            LLMJudgeService()
        )

    def _get_runtime_context(
        self,
        evaluation_input:
            EvaluationInput,
    ) -> tuple[
        Session,
        UUID,
        UUID | None,
    ]:
        db = (
            evaluation_input
            .metadata
            .get(
                "db"
            )
        )

        tenant_id = (
            evaluation_input
            .metadata
            .get(
                "tenant_id"
            )
        )

        evaluator_llm_configuration_id = (
            evaluation_input
            .metadata
            .get(
                "evaluator_llm_configuration_id"
            )
        )

        if db is None:
            raise ValueError(
                "Evaluation DB session "
                "was not provided."
            )

        if tenant_id is None:
            raise ValueError(
                "Evaluation tenant_id "
                "was not provided."
            )

        if not isinstance(
            tenant_id,
            UUID,
        ):
            tenant_id = UUID(
                str(
                    tenant_id
                )
            )

        if (
            evaluator_llm_configuration_id
            is not None
            and not isinstance(
                evaluator_llm_configuration_id,
                UUID,
            )
        ):
            evaluator_llm_configuration_id = (
                UUID(
                    str(
                        evaluator_llm_configuration_id
                    )
                )
            )

        return (
            db,
            tenant_id,
            evaluator_llm_configuration_id,
        )

    def _judge(
        self,
        evaluation_input:
            EvaluationInput,
    ) -> EvaluationMetricResult:
        (
            db,
            tenant_id,
            evaluator_llm_configuration_id,
        ) = self._get_runtime_context(
            evaluation_input
        )

        answerable = (
            evaluation_input
            .metadata
            .get(
                "answerable"
            )
        )

        judge_result = (
            self.judge_service.judge(
                db=db,

                tenant_id=
                    tenant_id,

                evaluator_llm_configuration_id=
                    evaluator_llm_configuration_id,

                metric_name=
                    self.metric_name,

                rubric=
                    self.rubric,

                question=
                    evaluation_input.question,

                actual_answer=
                    (
                        evaluation_input
                        .actual_answer
                        or ""
                    ),

                retrieved_context=
                    evaluation_input
                    .retrieved_context,

                expected_answer=
                    evaluation_input
                    .expected_answer,

                answerable=
                    answerable,

                threshold=
                    self.threshold,
            )
        )

        return (
            EvaluationMetricResult(
                metric_name=
                    self.metric_name,

                score=
                    judge_result.score,

                passed=
                    judge_result.passed,

                threshold=
                    self.threshold,

                reason=
                    judge_result.reason,

                evaluator_type=
                    self.evaluator_type,

                evaluator_engine=
                    self.evaluator_engine,

                metadata={
                    "usage":
                        judge_result.usage,

                    "latency_ms":
                        judge_result.latency_ms,

                    "evaluator":
                        judge_result
                        .evaluator_metadata,
                },
            )
        )


class FaithfulnessEvaluator(
    BaseLLMJudgeEvaluator
):
    """
    Measures whether factual claims in
    the generated answer are supported by
    the retrieved context.

    This metric does NOT compare against
    the expected answer.
    """

    metric_name = (
        "faithfulness"
    )

    threshold = 0.8

    rubric = """
Evaluate whether the Actual Answer is grounded in
the Retrieved Context.

A high score means:
- factual claims in the answer are supported by
  the retrieved context
- the answer does not invent facts
- the answer does not add unsupported details

A low score means:
- the answer contains claims not supported by
  the retrieved context
- the answer contradicts retrieved context
- the answer hallucinates information

Do NOT evaluate completeness or writing quality.
Do NOT use the Expected Answer to determine
faithfulness.
""".strip()

    def evaluate(
        self,
        evaluation_input:
            EvaluationInput,
    ) -> EvaluationMetricResult:
        if not (
            evaluation_input
            .actual_answer
        ):
            return (
                EvaluationMetricResult(
                    metric_name=
                        self.metric_name,

                    score=
                        0.0,

                    passed=
                        False,

                    threshold=
                        self.threshold,

                    reason=(
                        "No actual answer "
                        "was generated."
                    ),

                    evaluator_type=
                        self.evaluator_type,

                    evaluator_engine=
                        self.evaluator_engine,
                )
            )

        if not (
            evaluation_input
            .retrieved_context
        ):
            return (
                EvaluationMetricResult(
                    metric_name=
                        self.metric_name,

                    score=
                        0.0,

                    passed=
                        False,

                    threshold=
                        self.threshold,

                    reason=(
                        "No retrieved context "
                        "was available to "
                        "support the answer."
                    ),

                    evaluator_type=
                        self.evaluator_type,

                    evaluator_engine=
                        self.evaluator_engine,
                )
            )

        return (
            self._judge(
                evaluation_input
            )
        )


class AnswerRelevancyEvaluator(
    BaseLLMJudgeEvaluator
):
    """
    Measures whether the generated answer
    directly addresses the user's question.
    """

    metric_name = (
        "answer_relevancy"
    )

    threshold = 0.8

    rubric = """
Evaluate how directly and appropriately the
Actual Answer addresses the Question.

A high score means:
- the answer directly responds to the question
- the response stays on topic
- the answer avoids unnecessary unrelated content
- the answer is useful for the stated question

A low score means:
- the answer does not address the question
- the answer is mostly irrelevant
- the answer misunderstands the request
- the response contains excessive unrelated content

Do NOT evaluate factual correctness unless it
directly affects whether the answer addresses the
question.
""".strip()

    def evaluate(
        self,
        evaluation_input:
            EvaluationInput,
    ) -> EvaluationMetricResult:
        if not (
            evaluation_input
            .actual_answer
        ):
            return (
                EvaluationMetricResult(
                    metric_name=
                        self.metric_name,

                    score=
                        0.0,

                    passed=
                        False,

                    threshold=
                        self.threshold,

                    reason=(
                        "No actual answer "
                        "was generated."
                    ),

                    evaluator_type=
                        self.evaluator_type,

                    evaluator_engine=
                        self.evaluator_engine,
                )
            )

        return (
            self._judge(
                evaluation_input
            )
        )


class CorrectnessEvaluator(
    BaseLLMJudgeEvaluator
):
    """
    Measures semantic correctness of the
    actual answer against the golden answer.

    Only answerable golden cases should use
    this evaluator.
    """

    metric_name = (
        "correctness"
    )

    threshold = 0.8

    rubric = """
Compare the Actual Answer with the Expected Answer.

Evaluate semantic correctness, not exact wording.

A high score means:
- the important facts in the expected answer are
  correctly represented
- the actual answer does not contradict the
  expected answer
- differences in wording are acceptable when the
  meaning is equivalent

A lower score is appropriate when:
- important facts are wrong
- the answer contradicts the expected answer
- important required information is missing
- the answer materially changes the meaning

Do NOT require verbatim matching.
""".strip()

    def evaluate(
        self,
        evaluation_input:
            EvaluationInput,
    ) -> EvaluationMetricResult:
        answerable = (
            evaluation_input
            .metadata
            .get(
                "answerable",
                True,
            )
        )

        if not answerable:
            return (
                EvaluationMetricResult(
                    metric_name=
                        self.metric_name,

                    score=
                        None,

                    passed=
                        None,

                    threshold=
                        self.threshold,

                    reason=(
                        "Correctness is not "
                        "scored for an "
                        "unanswerable test case."
                    ),

                    evaluator_type=
                        self.evaluator_type,

                    evaluator_engine=
                        self.evaluator_engine,
                )
            )

        if not (
            evaluation_input
            .expected_answer
        ):
            return (
                EvaluationMetricResult(
                    metric_name=
                        self.metric_name,

                    score=
                        None,

                    passed=
                        None,

                    threshold=
                        self.threshold,

                    reason=(
                        "No expected answer "
                        "was configured."
                    ),

                    evaluator_type=
                        self.evaluator_type,

                    evaluator_engine=
                        self.evaluator_engine,
                )
            )

        if not (
            evaluation_input
            .actual_answer
        ):
            return (
                EvaluationMetricResult(
                    metric_name=
                        self.metric_name,

                    score=
                        0.0,

                    passed=
                        False,

                    threshold=
                        self.threshold,

                    reason=(
                        "No actual answer "
                        "was generated."
                    ),

                    evaluator_type=
                        self.evaluator_type,

                    evaluator_engine=
                        self.evaluator_engine,
                )
            )

        return (
            self._judge(
                evaluation_input
            )
        )


class RefusalCorrectnessEvaluator(
    BaseLLMJudgeEvaluator
):
    """
    Evaluates behavior on intentionally
    unanswerable golden cases.

    A good result means the model refuses,
    states that information is unavailable,
    or otherwise avoids inventing an answer.
    """

    metric_name = (
        "refusal_correctness"
    )

    threshold = 0.8

    rubric = """
The test case is intentionally marked as
unanswerable from the supplied knowledge.

Evaluate whether the Actual Answer handles this
correctly.

A high score means:
- the answer clearly indicates that the requested
  information is unavailable or unsupported
- the model avoids inventing facts
- the response may offer a safe next step without
  pretending to know the answer

A low score means:
- the answer fabricates information
- the answer confidently accepts a false premise
- the answer provides unsupported specific facts
- the answer implies knowledge that is not present

A concise grounded refusal should receive a high
score.
""".strip()

    def evaluate(
        self,
        evaluation_input:
            EvaluationInput,
    ) -> EvaluationMetricResult:
        answerable = (
            evaluation_input
            .metadata
            .get(
                "answerable",
                True,
            )
        )

        if answerable:
            return (
                EvaluationMetricResult(
                    metric_name=
                        self.metric_name,

                    score=
                        None,

                    passed=
                        None,

                    threshold=
                        self.threshold,

                    reason=(
                        "Refusal correctness "
                        "is only scored for "
                        "unanswerable cases."
                    ),

                    evaluator_type=
                        self.evaluator_type,

                    evaluator_engine=
                        self.evaluator_engine,
                )
            )

        if not (
            evaluation_input
            .actual_answer
        ):
            #
            # No answer is technically a safe
            # refusal, but not a very useful one.
            #
            return (
                EvaluationMetricResult(
                    metric_name=
                        self.metric_name,

                    score=
                        0.7,

                    passed=
                        False,

                    threshold=
                        self.threshold,

                    reason=(
                        "The model returned no "
                        "answer. It avoided "
                        "hallucination but did "
                        "not provide a useful "
                        "refusal."
                    ),

                    evaluator_type=
                        self.evaluator_type,

                    evaluator_engine=
                        self.evaluator_engine,
                )
            )

        return (
            self._judge(
                evaluation_input
            )
        )