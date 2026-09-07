import json
import logging

from uuid import UUID

from langchain_core.messages import (
    ToolMessage,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.agent import Agent
from app.models.agent_run import AgentRun
from app.models.agent_run_step import (
    AgentRunStep,
)
from app.models.tenant_llm_configuration import (
    TenantLLMConfiguration,
)
from app.services.online_eval_capture_service import (
    OnlineEvalCaptureService,
)


logger = logging.getLogger(
    "nxtgen.agent_online_eval"
)


class AgentOnlineEvalCaptureService:
    """
    Capture eligible Agent RAG interactions into
    the centralized Online Evaluation pipeline.

    Agent online-evaluation capture must not depend
    on OpenTelemetry being available.

    Preferred evidence:
    - raw search_knowledge ToolMessage content

    Durable fallback evidence:
    - persisted AgentRunStep TOOL output

    Preferred correlation:
    - production OpenTelemetry trace ID

    Durable fallback correlation:
    - AgentRun UUID hex, explicitly identified in
      evaluation_metadata as agent_run correlation.
    """

    def __init__(self):
        self.capture_service = (
            OnlineEvalCaptureService()
        )

    def _parse_tool_content(
        self,
        content,
    ) -> dict | None:
        if isinstance(
            content,
            dict,
        ):
            return content

        if not isinstance(
            content,
            str,
        ):
            return None

        clean_content = (
            content.strip()
        )

        if not clean_content:
            return None

        try:
            parsed = json.loads(
                clean_content
            )
        except (
            json.JSONDecodeError,
            TypeError,
        ):
            return None

        if not isinstance(
            parsed,
            dict,
        ):
            return None

        return parsed

    def _consume_search_payload(
        self,
        payload: dict,
        *,
        knowledge_base_id:
            UUID | None,
        contexts: list[str],
    ) -> tuple[
        UUID | None,
        list[str],
    ]:
        results = (
            payload.get(
                "results",
                [],
            )
            or []
        )

        for result in results:
            if not isinstance(
                result,
                dict,
            ):
                continue

            raw_kb_id = (
                result.get(
                    "knowledge_base_id"
                )
            )

            result_kb_id = None

            if raw_kb_id:
                try:
                    result_kb_id = UUID(
                        str(
                            raw_kb_id
                        )
                    )
                except (
                    ValueError,
                    TypeError,
                ):
                    result_kb_id = None

            if (
                knowledge_base_id
                is None
                and result_kb_id
                is not None
            ):
                knowledge_base_id = (
                    result_kb_id
                )

            text = str(
                result.get(
                    "text",
                    "",
                )
                or ""
            ).strip()

            if (
                text
                and text
                not in contexts
            ):
                contexts.append(
                    text
                )

        return (
            knowledge_base_id,
            contexts,
        )

    def _extract_rag_evidence(
        self,
        messages: list,
    ) -> tuple[
        UUID | None,
        list[str],
    ]:
        """
        Extract retrieval evidence from the raw
        search_knowledge ToolMessage.
        """

        knowledge_base_id: (
            UUID | None
        ) = None

        contexts: list[str] = []

        for message in messages:
            if not isinstance(
                message,
                ToolMessage,
            ):
                continue

            tool_name = str(
                getattr(
                    message,
                    "name",
                    "",
                )
                or ""
            ).strip()

            if (
                tool_name
                != "search_knowledge"
            ):
                continue

            payload = (
                self._parse_tool_content(
                    getattr(
                        message,
                        "content",
                        None,
                    )
                )
            )

            if not payload:
                continue

            (
                knowledge_base_id,
                contexts,
            ) = self._consume_search_payload(
                payload,
                knowledge_base_id=
                    knowledge_base_id,
                contexts=contexts,
            )

        return (
            knowledge_base_id,
            contexts,
        )

    def _extract_persisted_rag_evidence(
        self,
        db: Session,
        *,
        run: AgentRun,
    ) -> tuple[
        UUID | None,
        list[str],
    ]:
        """
        Durable fallback for Agent Chat.

        AgentExecutionService persists TOOL trace
        output into AgentRunStep.output_data. A
        search_knowledge step stores output as:

        {
            "results": [
                {
                    "name": "search_knowledge",
                    "content": "<json payload>"
                }
            ]
        }

        Flush first so newly added run steps from
        the current transaction can be queried
        before the outer transaction commits.
        """

        db.flush()

        steps = list(
            db.scalars(
                select(
                    AgentRunStep
                )
                .where(
                    AgentRunStep.run_id
                    == run.id
                )
                .order_by(
                    AgentRunStep
                    .step_number
                    .asc()
                )
            ).all()
        )

        knowledge_base_id: (
            UUID | None
        ) = None

        contexts: list[str] = []

        for step in steps:
            if str(
                getattr(
                    step.step_type,
                    "value",
                    step.step_type,
                )
            ).upper() != "TOOL":
                continue

            output_data = (
                step.output_data
                or {}
            )

            if not isinstance(
                output_data,
                dict,
            ):
                continue

            outputs = (
                output_data.get(
                    "results",
                    [],
                )
                or []
            )

            for output in outputs:
                if not isinstance(
                    output,
                    dict,
                ):
                    continue

                tool_name = str(
                    output.get(
                        "name",
                        "",
                    )
                    or ""
                ).strip()

                if (
                    tool_name
                    != "search_knowledge"
                ):
                    continue

                payload = (
                    self._parse_tool_content(
                        output.get(
                            "content"
                        )
                    )
                )

                if not payload:
                    continue

                (
                    knowledge_base_id,
                    contexts,
                ) = self._consume_search_payload(
                    payload,
                    knowledge_base_id=
                        knowledge_base_id,
                    contexts=contexts,
                )

        return (
            knowledge_base_id,
            contexts,
        )

    def capture_if_sampled(
        self,
        db: Session,
        *,
        agent: Agent,
        run: AgentRun,
        configuration:
            TenantLLMConfiguration,
        messages: list | None = None,
        source_trace_id:
            str | None = None,
    ) -> None:
        """
        Capture a completed Agent RAG interaction.

        Capture failure must never fail the
        successful Agent run.

        Online evaluation is an application feature,
        so an otherwise eligible Agent RAG sample is
        no longer discarded merely because an OTEL
        trace ID is unavailable.
        """

        if not settings.ONLINE_EVAL_ENABLED:
            logger.info(
                "Agent online evaluation skipped: "
                "disabled tenant=%s agent=%s run=%s",
                agent.tenant_id,
                agent.id,
                run.id,
            )
            return

        if not run.answer:
            logger.info(
                "Agent online evaluation skipped: "
                "no answer tenant=%s agent=%s run=%s",
                agent.tenant_id,
                agent.id,
                run.id,
            )
            return

        (
            knowledge_base_id,
            contexts,
        ) = self._extract_rag_evidence(
            messages
            or []
        )

        evidence_source = (
            "runtime_messages"
        )

        if (
            knowledge_base_id is None
            or not contexts
        ):
            (
                knowledge_base_id,
                contexts,
            ) = (
                self
                ._extract_persisted_rag_evidence(
                    db,
                    run=run,
                )
            )

            evidence_source = (
                "agent_run_steps"
            )

        if (
            knowledge_base_id is None
            or not contexts
        ):
            logger.info(
                "Agent online evaluation skipped: "
                "no RAG evidence "
                "tenant=%s agent=%s run=%s "
                "tools=%s",
                agent.tenant_id,
                agent.id,
                run.id,
                run.tools_used,
            )
            return

        try:
            should_sample = (
                self.capture_service
                .should_sample(
                    sample_rate=
                        settings
                        .ONLINE_EVAL_SAMPLE_RATE,
                )
            )

        except Exception:
            logger.exception(
                "Agent online evaluation sampling "
                "decision failed "
                "tenant=%s agent=%s run=%s",
                agent.tenant_id,
                agent.id,
                run.id,
            )
            return

        if not should_sample:
            logger.info(
                "Agent online evaluation skipped: "
                "sampling tenant=%s agent=%s run=%s "
                "rate=%s",
                agent.tenant_id,
                agent.id,
                run.id,
                settings
                .ONLINE_EVAL_SAMPLE_RATE,
            )
            return

        normalized_otel_trace_id = (
            str(
                source_trace_id
                or ""
            )
            .strip()
            .lower()
        )

        if normalized_otel_trace_id:
            resolved_trace_id = (
                normalized_otel_trace_id
            )
            correlation_kind = (
                "otel"
            )
        else:
            resolved_trace_id = (
                run.id.hex
            )
            correlation_kind = (
                "agent_run"
            )

            logger.info(
                "Agent online evaluation using "
                "AgentRun correlation because "
                "OTEL trace is unavailable "
                "tenant=%s agent=%s run=%s "
                "correlation=%s",
                agent.tenant_id,
                agent.id,
                run.id,
                resolved_trace_id,
            )

        try:
            with db.begin_nested():
                captured = (
                    self.capture_service
                    .capture(
                        db=db,
                        tenant_id=
                            agent.tenant_id,
                        knowledge_base_id=
                            knowledge_base_id,
                        conversation_id=
                            None,
                        message_id=
                            None,
                        question=
                            run.query,
                        actual_answer=
                            run.answer,
                        retrieval_context=
                            contexts,
                        generator_provider=
                            configuration
                            .provider
                            .value,
                        generator_model=
                            configuration
                            .model_name,
                        sample_reason=
                            "random",
                        source_trace_id=
                            resolved_trace_id,
                        evaluation_metadata={
                            "capture_source":
                                "agent",
                            "workload":
                                "agent",
                            "agent_id":
                                str(
                                    agent.id
                                ),
                            "agent_name":
                                agent.name,
                            "agent_run_id":
                                str(
                                    run.id
                                ),
                            "agent_thread_id":
                                (
                                    str(
                                        run.thread_id
                                    )
                                    if run.thread_id
                                    else None
                                ),
                            "actor_type":
                                run.actor_type,
                            "actor_id":
                                run.actor_id,
                            "sampling_rate":
                                settings
                                .ONLINE_EVAL_SAMPLE_RATE,
                            "rag_evidence_source":
                                evidence_source,
                            "source_trace_kind":
                                correlation_kind,
                            "otel_trace_id":
                                (
                                    normalized_otel_trace_id
                                    or None
                                ),
                        },
                    )
                )

            if captured is None:
                logger.warning(
                    "Agent online evaluation capture "
                    "returned no result "
                    "tenant=%s agent=%s run=%s "
                    "trace=%s",
                    agent.tenant_id,
                    agent.id,
                    run.id,
                    resolved_trace_id,
                )
                return

            logger.info(
                "Agent online evaluation candidate "
                "captured "
                "tenant=%s agent=%s run=%s "
                "kb=%s eval=%s trace=%s "
                "evidence=%s correlation=%s",
                agent.tenant_id,
                agent.id,
                run.id,
                knowledge_base_id,
                captured.id,
                resolved_trace_id,
                evidence_source,
                correlation_kind,
            )

        except Exception:
            logger.exception(
                "Agent online evaluation capture failed "
                "tenant=%s agent=%s run=%s "
                "trace=%s",
                agent.tenant_id,
                agent.id,
                run.id,
                resolved_trace_id,
            )
