import json
import logging

from uuid import UUID

from langchain_core.messages import (
    ToolMessage,
)
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.agent import Agent
from app.models.agent_run import AgentRun
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

    AgentRun trace remains audit evidence.
    Raw ToolMessage content is evaluation evidence.
    LLM usage trace_id is production trace correlation.
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

        Do not use AgentRun trace output because
        trace content is intentionally truncated
        for audit readability.
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

    def capture_if_sampled(
        self,
        db: Session,
        *,
        agent: Agent,
        run: AgentRun,
        configuration:
            TenantLLMConfiguration,
        messages: list,
        source_trace_id:
            str | None,
    ) -> None:
        """
        Capture a completed Agent RAG interaction.

        This is optional observability.
        Capture failure must never fail the
        successful Agent run.
        """

        if not settings.ONLINE_EVAL_ENABLED:
            return

        if not run.answer:
            return

        if not source_trace_id:
            logger.warning(
                "Agent online evaluation skipped: "
                "source trace unavailable "
                "tenant=%s agent=%s run=%s",
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
        )

        if (
            knowledge_base_id is None
            or not contexts
        ):
            logger.debug(
                "Agent online evaluation skipped: "
                "no RAG evidence "
                "tenant=%s agent=%s run=%s",
                agent.tenant_id,
                agent.id,
                run.id,
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
            return

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
                            source_trace_id,
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
                    source_trace_id,
                )
                return

            logger.info(
                "Agent online evaluation candidate "
                "captured "
                "tenant=%s agent=%s run=%s "
                "kb=%s eval=%s trace=%s",
                agent.tenant_id,
                agent.id,
                run.id,
                knowledge_base_id,
                captured.id,
                source_trace_id,
            )

        except Exception:
            logger.exception(
                "Agent online evaluation capture failed "
                "tenant=%s agent=%s run=%s "
                "trace=%s",
                agent.tenant_id,
                agent.id,
                run.id,
                source_trace_id,
            )
