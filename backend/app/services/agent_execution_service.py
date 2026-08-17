import logging
import time

from datetime import (
    datetime,
    timezone,
)
from uuid import UUID

from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy import (
    select,
)
from sqlalchemy.orm import Session

from app.agents.model_factory import (
    AgentModelFactory,
)
from app.agents.runtime import (
    AgentRuntime,
)
from app.agents.tool_registry import (
    AgentToolRegistry,
)
from app.core.enums import (
    AgentRunStatus,
    AgentRunStepStatus,
    AgentRunStepType,
    AgentStatus,
)
from app.models.agent import Agent
from app.models.agent_run import (
    AgentRun,
)
from app.models.agent_run_step import (
    AgentRunStep,
)
from app.models.tenant_llm_configuration import (
    TenantLLMConfiguration,
)
from app.models.user import User
from app.repositories.agent_repository import (
    AgentRepository,
)


logger = logging.getLogger(
    "nxtgen.agent_execution"
)


class AgentExecutionService:

    def __init__(self):
        self.agent_repository = (
            AgentRepository()
        )

        self.model_factory = (
            AgentModelFactory()
        )

        self.tool_registry = (
            AgentToolRegistry()
        )

        self.runtime = (
            AgentRuntime()
        )

    def _resolve_llm_configuration(
        self,
        db: Session,
        agent: Agent,
    ) -> TenantLLMConfiguration:

        if (
            agent.llm_configuration_id
            is not None
        ):
            configuration = db.get(
                TenantLLMConfiguration,
                agent.llm_configuration_id,
            )

            if (
                configuration is None
                or configuration.tenant_id
                != agent.tenant_id
            ):
                raise HTTPException(
                    status_code=
                        status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Agent LLM configuration "
                        "is invalid."
                    ),
                )

            if (
                not
                configuration.is_active
            ):
                raise HTTPException(
                    status_code=
                        status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Agent LLM configuration "
                        "is inactive."
                    ),
                )

            return configuration

        stmt = (
            select(
                TenantLLMConfiguration,
            )
            .where(
                TenantLLMConfiguration
                .tenant_id
                == agent.tenant_id,

                TenantLLMConfiguration
                .is_default
                .is_(True),

                TenantLLMConfiguration
                .is_active
                .is_(True),
            )
        )

        configuration = (
            db.scalars(
                stmt,
            )
            .first()
        )

        if configuration is None:
            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    "No active default LLM "
                    "configuration exists "
                    "for this tenant."
                ),
            )

        return configuration

    def _persist_trace(
        self,
        db: Session,
        run: AgentRun,
        trace: list[dict],
    ) -> None:

        for (
            index,
            trace_step,
        ) in enumerate(
            trace,
            start=1,
        ):
            step_type = (
                AgentRunStepType(
                    trace_step[
                        "step_type"
                    ]
                )
            )

            step_status = (
                AgentRunStepStatus(
                    trace_step.get(
                        "status",
                        "COMPLETED",
                    )
                )
            )

            step = AgentRunStep(
                run_id=
                    run.id,

                step_number=
                    index,

                step_type=
                    step_type,

                status=
                    step_status,

                name=
                    trace_step.get(
                        "name",
                        step_type.value,
                    ),

                input_data=
                    trace_step.get(
                        "input",
                    ),

                output_data=
                    trace_step.get(
                        "output",
                    ),

                duration_ms=
                    trace_step.get(
                        "duration_ms",
                    ),
            )

            db.add(
                step,
            )

    def run(
        self,
        db: Session,
        current_user: User,
        agent_id: UUID,
        query: str,
    ) -> dict:

        agent = (
            self.agent_repository
            .get_by_id_and_tenant(
                db=db,
                tenant_id=
                    current_user.tenant_id,
                agent_id=
                    agent_id,
            )
        )

        if agent is None:
            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,
                detail=(
                    "Agent not found."
                ),
            )

        if (
            agent.status
            != AgentStatus.ACTIVE
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Agent must be active "
                    "before it can run."
                ),
            )

        configuration = (
            self._resolve_llm_configuration(
                db=db,
                agent=agent,
            )
        )

        model = (
            self.model_factory.create(
                configuration,
            )
        )

        #
        # Resolve knowledge bases assigned
        # to this agent.
        #
        knowledge_base_ids = [
            link.knowledge_base_id
            for link
            in agent.knowledge_base_links
        ]

        #
        # Resolve dynamic tools assigned
        # to this agent.
        #
        tool_ids = [
            link.tool_id
            for link
            in agent.tool_links
        ]

        #
        # Build the final LangChain tool
        # collection.
        #
        # This currently supports:
        #
        # - native search_knowledge
        # - configured REST tools
        #
        # MCP tools will plug into this
        # same registry later.
        #
        tools = (
            self.tool_registry
            .get_tools(
                db=db,
                tenant_id=
                    agent.tenant_id,
                knowledge_base_ids=
                    knowledge_base_ids,
                tool_ids=
                    tool_ids,
            )
        )

        clean_query = (
            query.strip()
        )

        if not clean_query:
            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Agent query cannot "
                    "be empty."
                ),
            )

        run = AgentRun(
            tenant_id=
                agent.tenant_id,

            agent_id=
                agent.id,

            user_id=
                current_user.id,

            query=
                clean_query,

            status=
                AgentRunStatus.RUNNING,

            tools_used=[],

            llm_calls=0,
        )

        db.add(
            run,
        )

        db.commit()

        db.refresh(
            run,
        )

        run_id = (
            run.id
        )

        started_at = (
            time.perf_counter()
        )

        logger.info(
            "Agent execution started "
            "run=%s "
            "agent=%s "
            "tenant=%s "
            "user=%s "
            "model=%s "
            "knowledge_bases=%s "
            "assigned_tools=%s "
            "runtime_tools=%s",
            run_id,
            agent.id,
            agent.tenant_id,
            current_user.id,
            configuration.model_name,
            len(
                knowledge_base_ids
            ),
            len(
                tool_ids
            ),
            [
                tool.name
                for tool in tools
            ],
        )

        try:
            result = (
                self.runtime.run(
                    model=model,
                    tools=tools,
                    system_prompt=
                        agent.system_prompt,
                    query=
                        clean_query,
                    max_iterations=
                        agent.max_iterations,
                )
            )

            tools_used = []

            for message in (
                result[
                    "messages"
                ]
            ):
                tool_calls = (
                    getattr(
                        message,
                        "tool_calls",
                        None,
                    )
                )

                if not tool_calls:
                    continue

                for tool_call in (
                    tool_calls
                ):
                    tool_name = (
                        tool_call.get(
                            "name",
                        )
                    )

                    if (
                        tool_name
                        and tool_name
                        not in tools_used
                    ):
                        tools_used.append(
                            tool_name,
                        )

            self._persist_trace(
                db=db,
                run=run,
                trace=
                    result.get(
                        "trace",
                        [],
                    ),
            )

            duration_ms = (
                (
                    time.perf_counter()
                    - started_at
                )
                * 1000
            )

            run.answer = (
                result[
                    "answer"
                ]
            )

            run.status = (
                AgentRunStatus.COMPLETED
            )

            run.llm_calls = (
                result[
                    "llm_calls"
                ]
            )

            run.tools_used = (
                tools_used
            )

            run.duration_ms = (
                duration_ms
            )

            run.completed_at = (
                datetime.now(
                    timezone.utc,
                )
            )

            db.commit()

            logger.info(
                "Agent execution completed "
                "run=%s "
                "agent=%s "
                "llm_calls=%s "
                "tools_used=%s "
                "duration_ms=%.2f",
                run_id,
                agent.id,
                result[
                    "llm_calls"
                ],
                tools_used,
                duration_ms,
            )

            return {
                "run_id":
                    run_id,

                "answer":
                    result[
                        "answer"
                    ],

                "status":
                    AgentRunStatus.COMPLETED,

                "llm_calls":
                    result[
                        "llm_calls"
                    ],

                "tools_used":
                    tools_used,

                "duration_ms":
                    duration_ms,
            }

        except Exception as exc:
            db.rollback()

            duration_ms = (
                (
                    time.perf_counter()
                    - started_at
                )
                * 1000
            )

            failed_run = db.get(
                AgentRun,
                run_id,
            )

            if failed_run is not None:
                failed_run.status = (
                    AgentRunStatus.FAILED
                )

                failed_run.duration_ms = (
                    duration_ms
                )

                failed_run.error_message = (
                    str(
                        exc
                    )[
                        :2000
                    ]
                )

                failed_run.completed_at = (
                    datetime.now(
                        timezone.utc,
                    )
                )

                db.commit()

            logger.exception(
                "Agent execution failed "
                "run=%s "
                "agent=%s "
                "error_type=%s",
                run_id,
                agent.id,
                type(
                    exc
                ).__name__,
            )

            raise