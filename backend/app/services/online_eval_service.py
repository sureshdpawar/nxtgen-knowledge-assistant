import logging

from datetime import datetime, timezone
from uuid import UUID

from opentelemetry.trace import Status, StatusCode
from sqlalchemy.orm import Session

from app.core.telemetry import get_tracer
from app.models.online_eval_result import OnlineEvalResult
from app.repositories.online_eval_result_repository import OnlineEvalResultRepository
from app.services.llm_judge_service import JudgeResult, LLMJudgeService


logger = logging.getLogger("knowgentiq.online_eval")
tracer = get_tracer(__name__)


class OnlineEvalService:
    """
    Execute production quality evaluation for sampled RAG interactions.

    V1.1 keeps the original quality metrics and adds two diagnostic signals:

    - context answerability:
      can the question be answered from the retrieved evidence?
    - safe abstention:
      when the retrieved evidence is insufficient, did the model avoid
      inventing an answer and communicate the limitation appropriately?

    Important:
    context answerability is NOT a claim that the full knowledge base lacks
    the answer. It only evaluates the retrieved context supplied to the model.
    """

    FAITHFULNESS_THRESHOLD = 0.8
    ANSWER_RELEVANCY_THRESHOLD = 0.8
    CONTEXTUAL_RELEVANCY_THRESHOLD = 0.8
    CONTEXT_ANSWERABILITY_THRESHOLD = 0.8
    SAFE_ABSTENTION_THRESHOLD = 0.8

    FAITHFULNESS_RUBRIC = """
Evaluate whether the Actual Answer is grounded in the Retrieved Context.

A high score means:
- factual claims in the answer are supported by the retrieved context
- the answer does not invent facts
- the answer does not add unsupported details

A low score means:
- the answer contains claims not supported by the retrieved context
- the answer contradicts retrieved context
- the answer hallucinates information

Do NOT evaluate completeness or writing quality.
Do NOT use outside knowledge.
""".strip()

    ANSWER_RELEVANCY_RUBRIC = """
Evaluate how directly and appropriately the Actual Answer addresses the Question.

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

Do NOT use outside knowledge.
Do NOT evaluate retrieval quality in this metric.
""".strip()

    CONTEXTUAL_RELEVANCY_RUBRIC = """
Evaluate how relevant the Retrieved Context is to the Question.

A high score means:
- the retrieved context directly helps answer the question
- most supplied context is useful for the question
- irrelevant or distracting context is limited

A low score means:
- most retrieved context is unrelated
- the context does not provide useful evidence for answering the question
- the retrieved material is substantially noisy

Judge the Retrieved Context against the Question.
Do NOT evaluate the factual quality of the Actual Answer in this metric.
Do NOT use outside knowledge.
""".strip()

    CONTEXT_ANSWERABILITY_RUBRIC = """
Evaluate whether the Question can be answered from the Retrieved Context alone.

Return a high score when:
- the retrieved context contains enough evidence to answer the question
- the requested fact, policy, value, explanation, or relationship is present
  or can be directly supported by the supplied context

Return a low score when:
- the retrieved context does not contain the requested information
- answering would require guessing, unsupported inference, or outside knowledge
- the context is related to the topic but does not contain enough evidence to
  answer the actual question

Important:
- evaluate ONLY the supplied Retrieved Context
- do NOT infer whether the full knowledge base contains the answer
- do NOT use outside knowledge
- do NOT judge the quality of the Actual Answer
""".strip()

    SAFE_ABSTENTION_RUBRIC = """
The Retrieved Context has already been classified as insufficient to answer the
Question.

Evaluate whether the Actual Answer handles that situation safely and usefully.

A high score means:
- the answer does not invent unsupported facts
- the answer clearly communicates that the available information is insufficient
- the answer avoids pretending to know the requested fact
- the response remains relevant to the user's question

A low score means:
- the answer fabricates or guesses an answer
- the answer presents unsupported details as facts
- the answer gives a definitive answer despite insufficient evidence
- the response is unrelated or misleading

Do NOT use outside knowledge.
Do NOT reward a fabricated answer merely because it sounds helpful.
""".strip()

    def __init__(self):
        self.repository = OnlineEvalResultRepository()
        self.judge_service = LLMJudgeService()

    def _judge(
        self,
        db: Session,
        *,
        result: OnlineEvalResult,
        metric_name: str,
        rubric: str,
        threshold: float,
        evaluator_llm_configuration_id: UUID | None,
    ) -> JudgeResult:
        return self.judge_service.judge(
            db=db,
            tenant_id=result.tenant_id,
            evaluator_llm_configuration_id=evaluator_llm_configuration_id,
            metric_name=metric_name,
            rubric=rubric,
            question=result.question,
            actual_answer=result.actual_answer,
            retrieved_context=list(result.retrieval_context or []),
            expected_answer=None,
            answerable=None,
            threshold=threshold,
        )

    def _metric_metadata(self, judge_result: JudgeResult) -> dict:
        return {
            "score": judge_result.score,
            "passed": judge_result.passed,
            "reason": judge_result.reason,
            "usage": judge_result.usage,
            "latency_ms": judge_result.latency_ms,
            "evaluator": judge_result.evaluator_metadata,
        }

    def _total_cost(self, judge_results: list[JudgeResult]) -> dict:
        """
        Aggregate only known judge costs.

        Unknown pricing remains explicit and is never silently converted to zero.
        """
        total = 0.0
        currencies = set()
        priced_calls = 0
        unpriced_calls = 0

        for judge_result in judge_results:
            evaluator_metadata = judge_result.evaluator_metadata or {}
            cost = evaluator_metadata.get("cost") or {}

            if not cost.get("pricing_found", False):
                unpriced_calls += 1
                continue

            total_cost = cost.get("total_cost")
            currency = cost.get("currency")

            if total_cost is None:
                unpriced_calls += 1
                continue

            total += float(total_cost)
            priced_calls += 1

            if currency:
                currencies.add(str(currency))

        if priced_calls == 0:
            return {
                "pricing_complete": False,
                "total_cost": None,
                "currency": None,
                "priced_calls": 0,
                "unpriced_calls": unpriced_calls,
            }

        if len(currencies) > 1:
            return {
                "pricing_complete": False,
                "total_cost": None,
                "currency": None,
                "priced_calls": priced_calls,
                "unpriced_calls": unpriced_calls,
                "reason": "Judge calls used multiple currencies.",
            }

        currency = next(iter(currencies)) if currencies else None

        return {
            "pricing_complete": unpriced_calls == 0,
            "total_cost": round(total, 12),
            "currency": currency,
            "priced_calls": priced_calls,
            "unpriced_calls": unpriced_calls,
        }

    def evaluate_one(
        self,
        db: Session,
        *,
        result_id: UUID,
        evaluator_llm_configuration_id: UUID | None = None,
    ) -> OnlineEvalResult:
        """
        Evaluate one pending production sample.

        Status transitions:

            pending -> running -> completed

        On failure:

            running -> failed

        Evaluation routing:

        1. Determine whether the retrieved context can answer the question.
        2. Always measure faithfulness and contextual relevancy.
        3. If answerable:
             evaluate answer relevancy and use the original three-metric pass rule.
        4. If not answerable:
             evaluate safe abstention instead of answer relevancy.
             Contextual relevancy remains diagnostic and does not make a safe
             abstention fail by itself.
        """

        result = self.repository.get_pending(
            db=db,
            result_id=result_id,
        )

        if result is None:
            existing = self.repository.get(
                db=db,
                entity_id=result_id,
            )

            if existing is None:
                raise ValueError("Online evaluation result not found.")

            raise ValueError(
                "Online evaluation result is not pending "
                f"(status={existing.status})."
            )

        result.status = "running"
        result.error_message = None

        db.commit()
        db.refresh(result)

        with tracer.start_as_current_span("online_evaluation.run") as span:
            span.set_attribute("knowgentiq.tenant.id", str(result.tenant_id))

            if result.knowledge_base_id is not None:
                span.set_attribute(
                    "knowgentiq.knowledge_base.id",
                    str(result.knowledge_base_id),
                )

            span.set_attribute("knowgentiq.online_eval.id", str(result.id))
            span.set_attribute(
                "knowgentiq.source.trace_id",
                result.source_trace_id,
            )
            span.set_attribute(
                "knowgentiq.online_eval.sample_reason",
                result.sample_reason,
            )

            try:
                context_answerability = self._judge(
                    db=db,
                    result=result,
                    metric_name="context_answerability",
                    rubric=self.CONTEXT_ANSWERABILITY_RUBRIC,
                    threshold=self.CONTEXT_ANSWERABILITY_THRESHOLD,
                    evaluator_llm_configuration_id=evaluator_llm_configuration_id,
                )

                faithfulness = self._judge(
                    db=db,
                    result=result,
                    metric_name="faithfulness",
                    rubric=self.FAITHFULNESS_RUBRIC,
                    threshold=self.FAITHFULNESS_THRESHOLD,
                    evaluator_llm_configuration_id=evaluator_llm_configuration_id,
                )

                contextual_relevancy = self._judge(
                    db=db,
                    result=result,
                    metric_name="contextual_relevancy",
                    rubric=self.CONTEXTUAL_RELEVANCY_RUBRIC,
                    threshold=self.CONTEXTUAL_RELEVANCY_THRESHOLD,
                    evaluator_llm_configuration_id=evaluator_llm_configuration_id,
                )

                answer_relevancy: JudgeResult | None = None
                safe_abstention: JudgeResult | None = None

                metrics: dict[str, dict] = {
                    "context_answerability": self._metric_metadata(
                        context_answerability
                    ),
                    "faithfulness": self._metric_metadata(faithfulness),
                    "contextual_relevancy": self._metric_metadata(
                        contextual_relevancy
                    ),
                }

                judge_results = [
                    context_answerability,
                    faithfulness,
                    contextual_relevancy,
                ]

                if context_answerability.passed:
                    answer_relevancy = self._judge(
                        db=db,
                        result=result,
                        metric_name="answer_relevancy",
                        rubric=self.ANSWER_RELEVANCY_RUBRIC,
                        threshold=self.ANSWER_RELEVANCY_THRESHOLD,
                        evaluator_llm_configuration_id=(
                            evaluator_llm_configuration_id
                        ),
                    )

                    metrics["answer_relevancy"] = self._metric_metadata(
                        answer_relevancy
                    )
                    judge_results.append(answer_relevancy)

                    passed = all(
                        (
                            faithfulness.passed,
                            answer_relevancy.passed,
                            contextual_relevancy.passed,
                        )
                    )

                    evaluation_outcome = "pass" if passed else "fail"
                    evaluation_path = "answerable"

                else:
                    safe_abstention = self._judge(
                        db=db,
                        result=result,
                        metric_name="safe_abstention",
                        rubric=self.SAFE_ABSTENTION_RUBRIC,
                        threshold=self.SAFE_ABSTENTION_THRESHOLD,
                        evaluator_llm_configuration_id=(
                            evaluator_llm_configuration_id
                        ),
                    )

                    metrics["safe_abstention"] = self._metric_metadata(
                        safe_abstention
                    )
                    judge_results.append(safe_abstention)

                    passed = all(
                        (
                            faithfulness.passed,
                            safe_abstention.passed,
                        )
                    )

                    evaluation_outcome = (
                        "safe_abstention"
                        if passed
                        else "fail"
                    )
                    evaluation_path = "not_answerable_from_context"

                result.faithfulness_score = faithfulness.score

                result.answer_relevancy_score = (
                    answer_relevancy.score
                    if answer_relevancy is not None
                    else None
                )

                result.contextual_relevancy_score = (
                    contextual_relevancy.score
                )

                result.passed = passed
                result.evaluated_at = datetime.now(timezone.utc)

                existing_metadata = result.evaluation_metadata or {}

                result.evaluation_metadata = {
                    **existing_metadata,
                    "source_trace_id": result.source_trace_id,
                    "evaluation_path": evaluation_path,
                    "evaluation_outcome": evaluation_outcome,
                    "context_answerable": context_answerability.passed,
                    "metrics": metrics,
                    "judge_cost": self._total_cost(judge_results),
                }

                result.status = "completed"
                result.error_message = None

                span.set_attribute(
                    "knowgentiq.online_eval.context_answerable",
                    context_answerability.passed,
                )
                span.set_attribute(
                    "knowgentiq.online_eval.faithfulness_score",
                    faithfulness.score,
                )
                span.set_attribute(
                    "knowgentiq.online_eval.contextual_relevancy_score",
                    contextual_relevancy.score,
                )
                span.set_attribute(
                    "knowgentiq.online_eval.evaluation_path",
                    evaluation_path,
                )
                span.set_attribute(
                    "knowgentiq.online_eval.evaluation_outcome",
                    evaluation_outcome,
                )
                span.set_attribute(
                    "knowgentiq.online_eval.passed",
                    passed,
                )

                if answer_relevancy is not None:
                    span.set_attribute(
                        "knowgentiq.online_eval.answer_relevancy_score",
                        answer_relevancy.score,
                    )

                if safe_abstention is not None:
                    span.set_attribute(
                        "knowgentiq.online_eval.safe_abstention_score",
                        safe_abstention.score,
                    )

                span.set_status(Status(StatusCode.OK))

                db.commit()
                db.refresh(result)

                logger.info(
                    "Online evaluation completed "
                    "id=%s tenant=%s kb=%s source_trace_id=%s "
                    "path=%s outcome=%s passed=%s",
                    result.id,
                    result.tenant_id,
                    result.knowledge_base_id,
                    result.source_trace_id,
                    evaluation_path,
                    evaluation_outcome,
                    result.passed,
                )

                return result

            except Exception as exc:
                span.record_exception(exc)
                span.set_status(
                    Status(
                        StatusCode.ERROR,
                        str(exc),
                    )
                )

                db.rollback()

                failed_result = self.repository.get(
                    db=db,
                    entity_id=result_id,
                )

                if failed_result is not None:
                    failed_result.status = "failed"
                    failed_result.error_message = str(exc)
                    failed_result.evaluated_at = datetime.now(timezone.utc)
                    db.commit()

                logger.exception(
                    "Online evaluation failed id=%s",
                    result_id,
                )

                raise

    def process_pending(
        self,
        db: Session,
        *,
        tenant_id: UUID,
        limit: int = 10,
        evaluator_llm_configuration_id: UUID | None = None,
    ) -> dict:
        """
        Process a bounded batch of pending rows.

        This remains intentionally synchronous for the manual v1 workflow.
        """
        pending = self.repository.list_pending(
            db=db,
            tenant_id=tenant_id,
            limit=limit,
        )

        completed = 0
        failed = 0

        result_ids = [
            result.id
            for result in pending
        ]

        for result_id in result_ids:
            try:
                self.evaluate_one(
                    db=db,
                    result_id=result_id,
                    evaluator_llm_configuration_id=(
                        evaluator_llm_configuration_id
                    ),
                )
                completed += 1

            except Exception:
                failed += 1

        return {
            "selected": len(result_ids),
            "completed": completed,
            "failed": failed,
        }
