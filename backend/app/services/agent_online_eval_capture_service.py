import json
import logging

from uuid import UUID

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
    Capture eligible Agent RAG runs into the
    centralized Online Evaluation pipeline.

    This service does not run judges.
    """

    def __init__(self):
        self.capture_service = (
            OnlineEvalCaptureService()
        )

    def _extract_rag_evidence(
        self,
        trace: list[dict],
    ) -> tuple[
        UUID | None,
        list[str],
    ]:
        knowledge_base_id: (
            UUID | None
        ) = None

        contexts: list[str] = []

        for item in trace:
            if str(
                item.get(
                    "step_type",
                    "",
                )
            ).upper() != "TOOL":
                continue

            if (
                str(
                    item.get(
                        "name",
                        "",
                    )
                )
                != "search_knowledge"
            ):
                continue

            output = (
                item.get(
                    "output"
                )
                or {}
            )

            if not isinstance(
                output,
                dict,
            ):
                continue

            tool_results = (
                output.get(
                    "results",
                    []
                )
                or []
            )

            for tool_result in tool_results:
                if not isinstance(
                    tool_result,
                    dict,
                ):
                    continue

                content = (
                    tool_result.get(
                        "content"
                    )
                )

                payload = None

                if isinstance(
                    content,
                    str,
                ):
                    try:
                        payload = (
                            json.loads(
                                content
                            )
                        )
                    except (
                        json.JSONDecodeError,
                        TypeError,
                    ):
                        payload = None

                elif isinstance(
                    content,
                    dict,
                ):
                    payload = content

                if not isinstance(
                    payload,
                    dict,
                ):
                    continue

                results = (
                    payload.get(
                        "results",
                        []
                    )
                    or []
                )

                for result in results:
                    if not isinstance(
                        result,
                        dict,
                    ):
                        continue

                    if (
                        knowledge_base_id
                        is None
                    ):
                        raw_kb_id = (
                            result.get(
                                "knowledge_base_id"
                            )
                        )

                        if raw_kb_id:
                            try:
                                knowledge_base_id = (
                                    UUID(
                                        str(
                                            raw_kb_id
                                        )
                                    )
                                )
                            except ValueError:
                                pass

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
        trace: list[dict],
    ) -> None:
        if not settings.ONLINE_EVAL_ENABLED:
            return

        if not run.answer:
            return

        (
            knowledge_base_id,
            contexts,
        ) = self._extract_rag_evidence(
            trace
        )

        if (
            knowledge_base_id is None
            or not contexts
        ):
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
                "decision failed tenant=%s agent=%s run=%s",
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

            if captured is not None:
                logger.info(
                    "Agent online evaluation candidate "
                    "captured tenant=%s agent=%s run=%s "
                    "kb=%s eval=%s",
                    agent.tenant_id,
                    agent.id,
                    run.id,
                    knowledge_base_id,
                    captured.id,
                )

        except Exception:
            logger.exception(
                "Agent online evaluation capture failed "
                "tenant=%s agent=%s run=%s",
                agent.tenant_id,
                agent.id,
                run.id,
            )
