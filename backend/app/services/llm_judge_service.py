import json
import logging
import time

from dataclasses import (
    dataclass,
    field,
)
from uuid import UUID

from opentelemetry.trace import (
    Status,
    StatusCode,
)
from sqlalchemy.orm import Session

from app.core.telemetry import (
    get_tracer,
)
from app.services.llm_client_factory import (
    LLMClientFactory,
)
from app.services.llm_usage_service import (
    LLMUsageService,
)


logger = logging.getLogger(
    "nxtgen.eval.judge"
)

tracer = get_tracer(
    __name__
)


@dataclass
class JudgeResult:
    """
    Provider-neutral result returned by
    Knowgentiq LLM-as-a-Judge execution.
    """

    score: float

    passed: bool

    reason: str

    usage: dict = field(
        default_factory=dict,
    )

    latency_ms: float = 0.0

    evaluator_metadata: dict = field(
        default_factory=dict,
    )

    raw_response: dict = field(
        default_factory=dict,
    )


class LLMJudgeService:

    def __init__(self):
        self.client_factory = (
            LLMClientFactory()
        )

        self.llm_usage_service = (
            LLMUsageService()
        )

    def _estimate_tokens(
        self,
        text: str,
    ) -> int:
        if not text:
            return 0

        return max(
            1,
            len(text) // 4,
        )

    def _extract_json(
        self,
        content: str,
    ) -> dict:
        """
        Parse JSON returned by a judge.

        Supports:
        - plain JSON
        - fenced JSON
        - JSON surrounded by extra text
        """

        if not content:
            raise ValueError(
                "Evaluator returned "
                "an empty response."
            )

        cleaned = (
            content.strip()
        )

        if cleaned.startswith(
            "```json"
        ):
            cleaned = (
                cleaned[
                    len("```json"):
                ]
            )

        elif cleaned.startswith(
            "```"
        ):
            cleaned = (
                cleaned[
                    len("```"):
                ]
            )

        if cleaned.endswith(
            "```"
        ):
            cleaned = (
                cleaned[:-3]
            )

        cleaned = (
            cleaned.strip()
        )

        try:
            return json.loads(
                cleaned
            )

        except json.JSONDecodeError:
            pass

        start = cleaned.find(
            "{"
        )

        end = cleaned.rfind(
            "}"
        )

        if (
            start == -1
            or end == -1
            or end <= start
        ):
            raise ValueError(
                "Evaluator response did "
                "not contain valid JSON."
            )

        candidate = (
            cleaned[
                start:
                end + 1
            ]
        )

        try:
            return json.loads(
                candidate
            )

        except json.JSONDecodeError as exc:
            raise ValueError(
                "Unable to parse evaluator "
                "JSON response."
            ) from exc

    def _validate_result(
        self,
        payload: dict,
        threshold: float,
    ) -> tuple[
        float,
        bool,
        str,
    ]:
        if (
            "score"
            not in payload
        ):
            raise ValueError(
                "Evaluator response missing "
                "'score'."
            )

        try:
            score = float(
                payload[
                    "score"
                ]
            )

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "Evaluator score must "
                "be numeric."
            ) from exc

        score = max(
            0.0,
            min(
                1.0,
                score,
            ),
        )

        reason = str(
            payload.get(
                "reason",
                "",
            )
        ).strip()

        passed_value = (
            payload.get(
                "passed"
            )
        )

        if isinstance(
            passed_value,
            bool,
        ):
            passed = (
                passed_value
            )

        else:
            passed = (
                score
                >= threshold
            )

        return (
            score,
            passed,
            reason,
        )

    def _set_cost_span_attributes(
        self,
        span,
        usage_event,
    ) -> None:
        """
        Attach cost facts calculated by the
        central LLMUsageService.

        Pricing logic remains outside tracing.
        """

        if usage_event is None:
            return

        metadata = (
            usage_event.usage_metadata
            or {}
        )

        cost = (
            metadata.get(
                "cost"
            )
            or {}
        )

        pricing_found = bool(
            cost.get(
                "pricing_found",
                False,
            )
        )

        span.set_attribute(
            "knowgentiq.cost."
            "pricing_found",
            pricing_found,
        )

        if not pricing_found:
            return

        total_cost = (
            cost.get(
                "total_cost"
            )
        )

        if total_cost is not None:
            span.set_attribute(
                "knowgentiq.cost.total",
                float(
                    total_cost
                ),
            )

        currency = (
            cost.get(
                "currency"
            )
        )

        if currency:
            span.set_attribute(
                "knowgentiq.cost.currency",
                str(
                    currency
                ),
            )

        pricing_version = (
            cost.get(
                "pricing_version"
            )
        )

        if pricing_version:
            span.set_attribute(
                "knowgentiq.cost."
                "pricing_version",
                str(
                    pricing_version
                ),
            )

        pricing_source = (
            cost.get(
                "pricing_source"
            )
        )

        if pricing_source:
            span.set_attribute(
                "knowgentiq.cost."
                "pricing_source",
                str(
                    pricing_source
                ),
            )

    def judge(
        self,
        db: Session,
        tenant_id: UUID,
        metric_name: str,
        rubric: str,
        question: str,
        actual_answer: str,
        evaluator_llm_configuration_id:
            UUID | None = None,
        retrieved_context:
            list[str] | None = None,
        expected_answer:
            str | None = None,
        answerable:
            bool | None = None,
        threshold: float = 0.8,
    ) -> JudgeResult:
        """
        Run one LLM-as-a-Judge metric.

        evaluator_llm_configuration_id:

        - explicit profile -> use that profile
        - None -> use tenant default

        Each actual judge LLM call is:

        - traced as evaluation.judge
        - metered through LLMUsageService
        - costed by the central pricing layer
        """

        if (
            threshold < 0.0
            or threshold > 1.0
        ):
            raise ValueError(
                "Judge threshold must "
                "be between 0 and 1."
            )

        metric_name = (
            metric_name
            .strip()
        )

        if not metric_name:
            raise ValueError(
                "Judge metric name "
                "cannot be empty."
            )

        if not rubric.strip():
            raise ValueError(
                "Judge rubric "
                "cannot be empty."
            )

        retrieved_context = (
            retrieved_context
            or []
        )

        #
        # Resolve evaluator profile.
        #
        if (
            evaluator_llm_configuration_id
            is not None
        ):
            client, config = (
                self.client_factory
                .create_for_configuration(
                    db=db,

                    tenant_id=
                        tenant_id,

                    configuration_id=
                        evaluator_llm_configuration_id,
                )
            )

        else:
            client, config = (
                self.client_factory
                .create(
                    db=db,

                    tenant_id=
                        tenant_id,
                )
            )

        #
        # Format retrieved context.
        #
        if retrieved_context:
            context_text = "\n\n".join(
                [
                    (
                        f"[Context {index}]\n"
                        f"{context}"
                    )
                    for (
                        index,
                        context,
                    ) in enumerate(
                        retrieved_context,
                        start=1,
                    )
                ]
            )

        else:
            context_text = (
                "(no retrieved context provided)"
            )

        expected_answer_text = (
            expected_answer
            if expected_answer
            is not None
            else "(not provided)"
        )

        if answerable is None:
            answerable_text = (
                "(not provided)"
            )

        else:
            answerable_text = (
                "true"
                if answerable
                else "false"
            )

        prompt = f"""
You are an evaluation judge for an enterprise RAG system.

Evaluate ONLY the requested metric.

Metric:
{metric_name}

Rubric:
{rubric}

Question:
{question}

Expected Answer:
{expected_answer_text}

Expected Answerable:
{answerable_text}

Retrieved Context:
{context_text}

Actual Answer:
{actual_answer}

Return ONLY valid JSON using exactly this structure:

{{
  "score": 0.0,
  "passed": false,
  "reason": "Short explanation"
}}

Evaluation rules:

- score must be between 0.0 and 1.0
- 1.0 means the response fully satisfies the metric
- 0.0 means the response completely fails the metric
- evaluate only the requested metric
- do not introduce outside knowledge
- do not reward unsupported factual claims
- use only the supplied question, expected answer,
  answerability flag, context, and actual answer
- the reason must be concise and specific
""".strip()

        with tracer.start_as_current_span(
            "evaluation.judge"
        ) as span:
            span.set_attribute(
                "knowgentiq.tenant.id",
                str(
                    tenant_id
                ),
            )

            span.set_attribute(
                "knowgentiq.evaluation."
                "metric",
                metric_name,
            )

            span.set_attribute(
                "knowgentiq.evaluation."
                "threshold",
                threshold,
            )

            span.set_attribute(
                "gen_ai.system",
                str(
                    config.provider.value
                ),
            )

            span.set_attribute(
                "gen_ai.request.model",
                config.model_name,
            )

            span.set_attribute(
                "knowgentiq.llm.streaming",
                False,
            )

            started_at = (
                time.perf_counter()
            )

            try:
                response = (
                    client.chat.completions
                    .create(
                        model=
                            config.model_name,

                        messages=[
                            {
                                "role":
                                    "user",

                                "content":
                                    prompt,
                            }
                        ],

                        #
                        # Judge calls should be
                        # deterministic.
                        #
                        temperature=
                            0.0,

                        #
                        # Keep judge output compact.
                        #
                        max_tokens=
                            min(
                                config.max_tokens,
                                700,
                            ),
                    )
                )

                latency_ms = (
                    (
                        time.perf_counter()
                        - started_at
                    )
                    * 1000
                )

                content = ""

                if (
                    response.choices
                    and response
                    .choices[0]
                    .message
                ):
                    content = (
                        response
                        .choices[0]
                        .message
                        .content
                        or ""
                    )

                parsed = (
                    self._extract_json(
                        content
                    )
                )

                (
                    score,
                    passed,
                    reason,
                ) = self._validate_result(
                    payload=
                        parsed,

                    threshold=
                        threshold,
                )

                #
                # Judge usage.
                #
                if response.usage:
                    prompt_tokens = int(
                        response
                        .usage
                        .prompt_tokens
                        or 0
                    )

                    completion_tokens = int(
                        response
                        .usage
                        .completion_tokens
                        or 0
                    )

                    total_tokens = int(
                        response
                        .usage
                        .total_tokens
                        or (
                            prompt_tokens
                            + completion_tokens
                        )
                    )

                    usage_estimated = False

                else:
                    prompt_tokens = (
                        self._estimate_tokens(
                            prompt
                        )
                    )

                    completion_tokens = (
                        self._estimate_tokens(
                            content
                        )
                    )

                    total_tokens = (
                        prompt_tokens
                        + completion_tokens
                    )

                    usage_estimated = True

                usage = {
                    "prompt_tokens":
                        prompt_tokens,

                    "completion_tokens":
                        completion_tokens,

                    "total_tokens":
                        total_tokens,

                    "estimated":
                        usage_estimated,
                }

                #
                # Persist normalized evaluator
                # usage and calculate cost using
                # the same pricing path as chat.
                #
                usage_event = (
                    self.llm_usage_service
                    .record(
                        db=db,
                        tenant_id=
                            tenant_id,
                        knowledge_base_id=
                            None,
                        chat_channel_id=
                            None,
                        conversation_id=
                            None,
                        message_id=
                            None,
                        provider=
                            config.provider.value,
                        model=
                            config.model_name,
                        input_tokens=
                            prompt_tokens,
                        output_tokens=
                            completion_tokens,
                        request_type=
                            "eval",
                        usage_metadata={
                            "estimated":
                                usage_estimated,

                            "streaming":
                                False,

                            "evaluation_metric":
                                metric_name,

                            "evaluation_role":
                                "judge",
                        },
                    )
                )

                span.set_attribute(
                    "gen_ai.usage.input_tokens",
                    prompt_tokens,
                )

                span.set_attribute(
                    "gen_ai.usage.output_tokens",
                    completion_tokens,
                )

                span.set_attribute(
                    "knowgentiq.llm."
                    "total_tokens",
                    total_tokens,
                )

                span.set_attribute(
                    "knowgentiq.llm."
                    "usage_estimated",
                    usage_estimated,
                )

                span.set_attribute(
                    "knowgentiq.evaluation."
                    "score",
                    score,
                )

                span.set_attribute(
                    "knowgentiq.evaluation."
                    "passed",
                    passed,
                )

                span.set_attribute(
                    "knowgentiq.evaluation."
                    "latency_ms",
                    round(
                        latency_ms,
                        2,
                    ),
                )

                self._set_cost_span_attributes(
                    span,
                    usage_event,
                )

                span.set_status(
                    Status(
                        StatusCode.OK
                    )
                )

            except Exception as exc:
                span.record_exception(
                    exc
                )

                span.set_status(
                    Status(
                        StatusCode.ERROR,
                        str(
                            exc
                        ),
                    )
                )

                raise

        evaluator_metadata = {
            "profile_id":
                str(
                    config.id
                ),

            "profile_name":
                config.name,

            "provider":
                config.provider.value,

            "model":
                config.model_name,

            "metric_name":
                metric_name,

            "threshold":
                threshold,
        }

        #
        # Surface cost metadata to the
        # experiment aggregation layer without
        # duplicating calculation logic.
        #
        usage_event_metadata = (
            usage_event.usage_metadata
            or {}
        )

        cost_metadata = (
            usage_event_metadata.get(
                "cost"
            )
        )

        if cost_metadata:
            evaluator_metadata[
                "cost"
            ] = cost_metadata

        logger.info(
            "Evaluation judge completed "
            "metric='%s' "
            "score=%.3f "
            "passed=%s "
            "model='%s' "
            "latency_ms=%.2f",
            metric_name,
            score,
            passed,
            config.model_name,
            latency_ms,
        )

        return JudgeResult(
            score=
                score,

            passed=
                passed,

            reason=
                reason,

            usage=
                usage,

            latency_ms=
                round(
                    latency_ms,
                    2,
                ),

            evaluator_metadata=
                evaluator_metadata,

            raw_response=
                parsed,
        )
