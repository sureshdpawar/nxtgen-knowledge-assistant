import logging
import time

from collections.abc import (
    Awaitable,
    Callable,
)
from datetime import (
    datetime,
    timezone,
)
from typing import Any
from uuid import (
    UUID,
    uuid4,
)

from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.orm import Session

from app.agents.checkpointing import (
    agent_checkpointer,
)
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
from app.services.llm_usage_service import (
    LLMUsageService,
)


logger = logging.getLogger(
    "nxtgen.agent_execution"
)


ProgressCallback = Callable[
    [dict[str, Any]],
    Awaitable[None] | None,
]


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
        self.llm_usage_service = (
            LLMUsageService()
        )

    async def _emit_progress(
        self,
        progress_callback:
            ProgressCallback | None,
        event: dict[str, Any],
    ) -> None:
        if progress_callback is None:
            return

        result = progress_callback(
            event,
        )

        if (
            result is not None
            and hasattr(
                result,
                "__await__",
            )
        ):
            await result

    def _scoped_thread_id(
        self,
        *,
        tenant_id: UUID,
        agent_id: UUID,
        user_id: UUID,
        thread_id: UUID,
    ) -> str:
        return (
            f"{tenant_id}:"
            f"{agent_id}:"
            f"{user_id}:"
            f"{thread_id}"
        )

    def _get_agent(
        self,
        db: Session,
        *,
        current_user: User,
        agent_id: UUID,
    ) -> Agent:
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
                detail=
                    "Agent not found.",
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

        return agent

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
                or not
                configuration.is_active
            ):
                raise HTTPException(
                    status_code=
                        status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Agent LLM configuration "
                        "is invalid or inactive."
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

    async def _runtime_dependencies(
        self,
        db: Session,
        agent: Agent,
    ):
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

        knowledge_base_ids = [
            link.knowledge_base_id
            for link
            in agent.knowledge_base_links
        ]

        tool_ids = [
            link.tool_id
            for link
            in agent.tool_links
        ]

        tools = (
            await
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

        return (
            configuration,
            model,
            tools,
        )

    def _persist_trace(
        self,
        db: Session,
        run: AgentRun,
        trace: list[dict],
    ) -> None:
        if not trace:
            return

        last_step = (
            db.scalar(
                select(
                    func.max(
                        AgentRunStep
                        .step_number
                    )
                )
                .where(
                    AgentRunStep.run_id
                    == run.id
                )
            )
            or 0
        )

        for offset, item in enumerate(
            trace,
            start=1,
        ):
            step_type = (
                AgentRunStepType(
                    item[
                        "step_type"
                    ]
                )
            )

            db.add(
                AgentRunStep(
                    run_id=
                        run.id,
                    step_number=
                        last_step
                        + offset,
                    step_type=
                        step_type,
                    status=
                        AgentRunStepStatus(
                            item.get(
                                "status",
                                "COMPLETED",
                            )
                        ),
                    name=
                        item.get(
                            "name",
                            step_type.value,
                        ),
                    input_data=
                        item.get(
                            "input"
                        ),
                    output_data=
                        item.get(
                            "output"
                        ),
                    duration_ms=
                        item.get(
                            "duration_ms"
                        ),
                )
            )

    def _extract_llm_usage(
        self,
        message,
    ) -> tuple[
        int,
        int,
    ] | None:
        usage_metadata = (
            getattr(
                message,
                "usage_metadata",
                None,
            )
            or {}
        )

        input_tokens = (
            usage_metadata.get(
                "input_tokens"
            )
        )
        output_tokens = (
            usage_metadata.get(
                "output_tokens"
            )
        )

        if (
            input_tokens is not None
            and output_tokens is not None
        ):
            return (
                int(
                    input_tokens
                ),
                int(
                    output_tokens
                ),
            )

        response_metadata = (
            getattr(
                message,
                "response_metadata",
                None,
            )
            or {}
        )

        token_usage = (
            response_metadata.get(
                "token_usage"
            )
            or response_metadata.get(
                "usage"
            )
            or {}
        )

        input_tokens = (
            token_usage.get(
                "prompt_tokens"
            )
        )
        output_tokens = (
            token_usage.get(
                "completion_tokens"
            )
        )

        if (
            input_tokens is None
            or output_tokens is None
        ):
            return None

        return (
            int(
                input_tokens
            ),
            int(
                output_tokens
            ),
        )

    def _record_agent_llm_usage(
        self,
        db: Session,
        *,
        agent: Agent,
        run: AgentRun,
        configuration:
            TenantLLMConfiguration,
        messages: list,
    ) -> int:
        recorded = 0

        for message in messages:
            usage = (
                self._extract_llm_usage(
                    message
                )
            )

            if usage is None:
                continue

            (
                input_tokens,
                output_tokens,
            ) = usage

            recorded += 1

            self.llm_usage_service.record(
                db=db,
                tenant_id=
                    agent.tenant_id,
                provider=
                    configuration
                    .provider
                    .value,
                model=
                    configuration
                    .model_name,
                input_tokens=
                    input_tokens,
                output_tokens=
                    output_tokens,
                knowledge_base_id=
                    None,
                request_type=
                    "agent",
                usage_metadata={
                    "estimated":
                        False,
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
                    "agent_llm_call":
                        recorded,
                },
            )

        return recorded

    def _tools_used(
        self,
        messages: list,
    ) -> list[str]:
        names: list[
            str
        ] = []

        for message in messages:
            for call in (
                getattr(
                    message,
                    "tool_calls",
                    None,
                )
                or []
            ):
                name = call.get(
                    "name"
                )

                if (
                    name
                    and name
                    not in names
                ):
                    names.append(
                        name
                    )

        return names

    async def run(
        self,
        db: Session,
        current_user: User,
        agent_id: UUID,
        query: str,
        thread_id: UUID | None = None,
        progress_callback:
            ProgressCallback | None = None,
    ) -> dict:
        agent = self._get_agent(
            db,
            current_user=
                current_user,
            agent_id=
                agent_id,
        )

        clean_query = query.strip()

        if not clean_query:
            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Agent query cannot "
                    "be empty."
                ),
            )

        public_thread_id = (
            thread_id
            or uuid4()
        )

        (
            configuration,
            model,
            tools,
        ) = await self._runtime_dependencies(
            db,
            agent,
        )

        run = AgentRun(
            tenant_id=
                agent.tenant_id,
            agent_id=
                agent.id,
            user_id=
                current_user.id,
            thread_id=
                public_thread_id,
            query=
                clean_query,
            status=
                AgentRunStatus.RUNNING,
            tools_used=[],
            llm_calls=0,
        )

        db.add(
            run
        )
        db.commit()
        db.refresh(
            run
        )

        started_at = (
            time.perf_counter()
        )

        scoped_thread = (
            self._scoped_thread_id(
                tenant_id=
                    agent.tenant_id,
                agent_id=
                    agent.id,
                user_id=
                    current_user.id,
                thread_id=
                    public_thread_id,
            )
        )

        try:
            async with (
                agent_checkpointer()
            ) as checkpointer:
                result = (
                    await
                    self.runtime.run_turn(
                        model=model,
                        tools=tools,
                        system_prompt=
                            agent.system_prompt,
                        query=
                            clean_query,
                        max_iterations=
                            agent.max_iterations,
                        checkpointer=
                            checkpointer,
                        thread_id=
                            scoped_thread,
                        run_id=
                            str(
                                run.id
                            ),
                        progress_callback=
                            progress_callback,
                    )
                )

            duration_ms = (
                (
                    time.perf_counter()
                    - started_at
                )
                * 1000
            )

            self._persist_trace(
                db,
                run,
                result[
                    "trace"
                ],
            )

            self._record_agent_llm_usage(
                db,
                agent=agent,
                run=run,
                configuration=
                    configuration,
                messages=
                    result[
                        "new_messages"
                    ],
            )

            tools_used = (
                self._tools_used(
                    result[
                        "new_messages"
                    ]
                )
            )

            run.checkpoint_id = (
                result[
                    "checkpoint_id"
                ]
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

            if result[
                "interrupted"
            ]:
                run.status = (
                    AgentRunStatus
                    .WAITING_FOR_APPROVAL
                )

                db.commit()

                return {
                    "run_id":
                        run.id,
                    "thread_id":
                        public_thread_id,
                    "checkpoint_id":
                        run.checkpoint_id,
                    "answer":
                        None,
                    "status":
                        run.status,
                    "llm_calls":
                        run.llm_calls,
                    "tools_used":
                        tools_used,
                    "duration_ms":
                        duration_ms,
                    "interrupts":
                        result[
                            "interrupts"
                        ],
                }

            run.answer = (
                result[
                    "answer"
                ]
            )
            run.status = (
                AgentRunStatus.COMPLETED
            )
            run.completed_at = (
                datetime.now(
                    timezone.utc,
                )
            )

            db.commit()

            return {
                "run_id":
                    run.id,
                "thread_id":
                    public_thread_id,
                "checkpoint_id":
                    run.checkpoint_id,
                "answer":
                    run.answer,
                "status":
                    run.status,
                "llm_calls":
                    run.llm_calls,
                "tools_used":
                    tools_used,
                "duration_ms":
                    duration_ms,
                "interrupts":
                    [],
            }

        except Exception as exc:
            db.rollback()

            failed_run = db.get(
                AgentRun,
                run.id,
            )

            if failed_run is not None:
                failed_run.status = (
                    AgentRunStatus.FAILED
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

            raise

    async def resume(
        self,
        db: Session,
        current_user: User,
        agent_id: UUID,
        run_id: UUID,
        *,
        decision: str,
        reason: str | None = None,
        progress_callback:
            ProgressCallback | None = None,
    ) -> dict:
        agent = self._get_agent(
            db,
            current_user=
                current_user,
            agent_id=
                agent_id,
        )

        run = db.get(
            AgentRun,
            run_id,
        )

        if (
            run is None
            or run.tenant_id
            != current_user.tenant_id
            or run.agent_id
            != agent.id
            or run.user_id
            != current_user.id
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,
                detail=
                    "Agent run not found.",
            )

        if (
            run.status
            != AgentRunStatus
            .WAITING_FOR_APPROVAL
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,
                detail=(
                    "Agent run is not waiting "
                    "for human approval."
                ),
            )

        if run.thread_id is None:
            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,
                detail=(
                    "Agent run has no "
                    "LangGraph thread."
                ),
            )

        (
            configuration,
            model,
            tools,
        ) = await self._runtime_dependencies(
            db,
            agent,
        )

        scoped_thread = (
            self._scoped_thread_id(
                tenant_id=
                    agent.tenant_id,
                agent_id=
                    agent.id,
                user_id=
                    current_user.id,
                thread_id=
                    run.thread_id,
            )
        )

        started_at = (
            time.perf_counter()
        )

        try:
            async with (
                agent_checkpointer()
            ) as checkpointer:
                result = (
                    await
                    self.runtime.resume(
                        model=model,
                        tools=tools,
                        system_prompt=
                            agent.system_prompt,
                        max_iterations=
                            agent.max_iterations,
                        checkpointer=
                            checkpointer,
                        thread_id=
                            scoped_thread,
                        decision={
                            "decision":
                                decision,
                            "reason":
                                reason,
                        },
                        progress_callback=
                            progress_callback,
                    )
                )

            duration_ms = (
                (
                    time.perf_counter()
                    - started_at
                )
                * 1000
            )

            self._persist_trace(
                db,
                run,
                result[
                    "trace"
                ],
            )

            self._record_agent_llm_usage(
                db,
                agent=agent,
                run=run,
                configuration=
                    configuration,
                messages=
                    result[
                        "new_messages"
                    ],
            )

            resumed_tools = (
                self._tools_used(
                    result[
                        "new_messages"
                    ]
                )
            )

            merged_tools = list(
                run.tools_used
                or []
            )

            for name in resumed_tools:
                if name not in merged_tools:
                    merged_tools.append(
                        name
                    )

            run.checkpoint_id = (
                result[
                    "checkpoint_id"
                ]
            )
            run.llm_calls = (
                result[
                    "llm_calls"
                ]
            )
            run.tools_used = (
                merged_tools
            )
            run.duration_ms = (
                (
                    run.duration_ms
                    or 0
                )
                + duration_ms
            )

            if result[
                "interrupted"
            ]:
                run.status = (
                    AgentRunStatus
                    .WAITING_FOR_APPROVAL
                )

                db.commit()

                return {
                    "run_id":
                        run.id,
                    "thread_id":
                        run.thread_id,
                    "checkpoint_id":
                        run.checkpoint_id,
                    "answer":
                        None,
                    "status":
                        run.status,
                    "llm_calls":
                        run.llm_calls,
                    "tools_used":
                        merged_tools,
                    "duration_ms":
                        run.duration_ms,
                    "interrupts":
                        result[
                            "interrupts"
                        ],
                }

            run.answer = (
                result[
                    "answer"
                ]
            )
            run.status = (
                AgentRunStatus.COMPLETED
            )
            run.completed_at = (
                datetime.now(
                    timezone.utc,
                )
            )

            db.commit()

            return {
                "run_id":
                    run.id,
                "thread_id":
                    run.thread_id,
                "checkpoint_id":
                    run.checkpoint_id,
                "answer":
                    run.answer,
                "status":
                    run.status,
                "llm_calls":
                    run.llm_calls,
                "tools_used":
                    merged_tools,
                "duration_ms":
                    run.duration_ms,
                "interrupts":
                    [],
            }

        except Exception as exc:
            db.rollback()

            run = db.get(
                AgentRun,
                run_id,
            )

            if run is not None:
                run.status = (
                    AgentRunStatus.FAILED
                )
                run.error_message = (
                    str(
                        exc
                    )[
                        :2000
                    ]
                )
                run.completed_at = (
                    datetime.now(
                        timezone.utc,
                    )
                )
                db.commit()

            raise

    def _assert_thread_access(
        self,
        db: Session,
        *,
        current_user: User,
        agent: Agent,
        thread_id: UUID,
    ) -> None:
        existing = db.scalar(
            select(AgentRun.id)
            .where(
                AgentRun.tenant_id == current_user.tenant_id,
                AgentRun.agent_id == agent.id,
                AgentRun.user_id == current_user.id,
                AgentRun.thread_id == thread_id,
            )
            .limit(1)
        )

        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent thread not found.",
            )

    async def get_graph_state(
        self,
        db: Session,
        current_user: User,
        agent_id: UUID,
        thread_id: UUID,
    ) -> dict:
        agent = self._get_agent(
            db,
            current_user=current_user,
            agent_id=agent_id,
        )

        self._assert_thread_access(
            db,
            current_user=current_user,
            agent=agent,
            thread_id=thread_id,
        )

        _, model, tools = await self._runtime_dependencies(
            db,
            agent,
        )

        scoped_thread = self._scoped_thread_id(
            tenant_id=agent.tenant_id,
            agent_id=agent.id,
            user_id=current_user.id,
            thread_id=thread_id,
        )

        async with agent_checkpointer() as checkpointer:
            return await self.runtime.inspect_state(
                model=model,
                tools=tools,
                system_prompt=agent.system_prompt,
                max_iterations=agent.max_iterations,
                checkpointer=checkpointer,
                thread_id=scoped_thread,
            )

    async def get_checkpoint_history(
        self,
        db: Session,
        current_user: User,
        agent_id: UUID,
        thread_id: UUID,
        limit: int = 20,
    ) -> list[dict]:
        agent = self._get_agent(
            db,
            current_user=current_user,
            agent_id=agent_id,
        )

        self._assert_thread_access(
            db,
            current_user=current_user,
            agent=agent,
            thread_id=thread_id,
        )

        _, model, tools = await self._runtime_dependencies(
            db,
            agent,
        )

        scoped_thread = self._scoped_thread_id(
            tenant_id=agent.tenant_id,
            agent_id=agent.id,
            user_id=current_user.id,
            thread_id=thread_id,
        )

        async with agent_checkpointer() as checkpointer:
            return await self.runtime.checkpoint_history(
                model=model,
                tools=tools,
                system_prompt=agent.system_prompt,
                max_iterations=agent.max_iterations,
                checkpointer=checkpointer,
                thread_id=scoped_thread,
                limit=max(1, min(limit, 100)),
            )

