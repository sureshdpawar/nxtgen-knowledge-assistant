from __future__ import annotations

import inspect
import json
import logging
import time

from collections.abc import Awaitable, Callable
from typing import Any

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.types import Command, interrupt

from app.agents.state import AgentState
from app.agents.tool_execution_policy import (
    ToolExecutionPolicy,
    ToolExecutionPolicyContext,
    ToolExecutionPolicyResolver,
)


logger = logging.getLogger(
    "nxtgen.agent_runtime"
)

MAX_TRACE_OUTPUT_LENGTH = 4000

ProgressCallback = Callable[
    [dict[str, Any]],
    Awaitable[None] | None,
]


class AgentRuntime:

    def __init__(self):
        self.tool_execution_policy_resolver = (
            ToolExecutionPolicyResolver()
        )

    async def _emit(
        self,
        callback: ProgressCallback | None,
        event: dict[str, Any],
    ) -> None:
        if callback is None:
            return

        result = callback(event)

        if inspect.isawaitable(result):
            await result

    def _safe_output(
        self,
        value,
    ) -> str:
        text = str(value)

        if len(text) <= MAX_TRACE_OUTPUT_LENGTH:
            return text

        return (
            text[:MAX_TRACE_OUTPUT_LENGTH]
            + "...[truncated]"
        )

    def _tool_risk_level(
        self,
        tool: BaseTool,
    ) -> str:
        metadata = (
            getattr(
                tool,
                "metadata",
                None,
            )
            or {}
        )

        governance = (
            metadata.get(
                "knowgentiq",
                {},
            )
            or {}
        )

        return str(
            governance.get(
                "risk_level",
                "READ",
            )
        ).upper()

    def _checkpoint_id(
        self,
        snapshot,
    ) -> str | None:
        if snapshot is None:
            return None

        config = (
            getattr(
                snapshot,
                "config",
                None,
            )
            or {}
        )

        configurable = (
            config.get(
                "configurable",
                {},
            )
            or {}
        )

        value = configurable.get(
            "checkpoint_id"
        )

        return (
            str(value)
            if value
            else None
        )

    def _interrupt_payloads(
        self,
        snapshot,
    ) -> list[dict]:
        payloads: list[dict] = []

        if snapshot is None:
            return payloads

        for task in (
            getattr(
                snapshot,
                "tasks",
                (),
            )
            or ()
        ):
            for item in (
                getattr(
                    task,
                    "interrupts",
                    (),
                )
                or ()
            ):
                value = getattr(
                    item,
                    "value",
                    None,
                )

                if isinstance(
                    value,
                    dict,
                ):
                    payloads.append(value)
                else:
                    payloads.append(
                        {
                            "value":
                                value,
                        }
                    )

        return payloads

    async def _build_graph(
        self,
        *,
        model,
        tools: list[BaseTool],
        system_prompt: str,
        max_iterations: int,
        checkpointer,
        progress_callback:
            ProgressCallback | None,
        auto_execute_tool_names:
            set[str] | None = None,
    ):
        if tools:
            model_with_tools = (
                model.bind_tools(
                    tools,
                )
            )

            langgraph_tool_node = (
                ToolNode(
                    tools,
                )
            )
        else:
            model_with_tools = model
            langgraph_tool_node = None

        risk_by_tool_name = {
            tool.name:
                self._tool_risk_level(
                    tool
                )
            for tool in tools
        }

        execution_policy_context = (
            ToolExecutionPolicyContext
            .from_auto_execute_tool_names(
                auto_execute_tool_names
            )
        )

        policy_by_tool_name = {
            tool.name:
                self
                .tool_execution_policy_resolver
                .resolve(
                    tool_name=
                        tool.name,
                    risk_level=
                        risk_by_tool_name.get(
                            tool.name,
                            "READ",
                        ),
                    context=
                        execution_policy_context,
                )
            for tool in tools
        }

        async def call_model(
            state: AgentState,
        ):
            llm_calls = (
                state.get(
                    "llm_calls",
                    0,
                )
            )

            if llm_calls >= max_iterations:
                return {
                    "llm_calls":
                        llm_calls,
                }

            messages = [
                SystemMessage(
                    content=
                        system_prompt,
                ),
                *state[
                    "messages"
                ],
            ]

            iteration = (
                llm_calls + 1
            )

            await self._emit(
                progress_callback,
                {
                    "type":
                        "llm_started",
                    "iteration":
                        iteration,
                },
            )

            started_at = (
                time.perf_counter()
            )

            response = (
                await
                model_with_tools
                .ainvoke(
                    messages,
                )
            )

            duration_ms = (
                (
                    time.perf_counter()
                    - started_at
                )
                * 1000
            )

            tool_calls = (
                getattr(
                    response,
                    "tool_calls",
                    None,
                )
                or []
            )

            requested_tools = [
                {
                    "name":
                        tool_call.get(
                            "name",
                        ),

                    "args":
                        tool_call.get(
                            "args",
                            {},
                        ),

                    "risk_level":
                        risk_by_tool_name.get(
                            tool_call.get(
                                "name",
                                "",
                            ),
                            "READ",
                        ),

                    "execution_policy":
                        policy_by_tool_name.get(
                            tool_call.get(
                                "name",
                                "",
                            ),
                            ToolExecutionPolicy.AUTO,
                        ).value,
                }
                for tool_call
                in tool_calls
            ]

            await self._emit(
                progress_callback,
                {
                    "type":
                        "llm_completed",

                    "iteration":
                        iteration,

                    "duration_ms":
                        duration_ms,

                    "has_tool_calls":
                        bool(
                            tool_calls
                        ),

                    "tools":
                        [
                            item["name"]
                            for item
                            in requested_tools
                            if item["name"]
                        ],
                },
            )

            return {
                "messages": [
                    response,
                ],

                "llm_calls":
                    iteration,

                "trace": [
                    {
                        "step_type":
                            "LLM",

                        "name":
                            "llm",

                        "status":
                            "COMPLETED",

                        "input":
                            {
                                "iteration":
                                    iteration,

                                "message_count":
                                    len(
                                        messages,
                                    ),
                            },

                        "output":
                            {
                                "response_type":
                                    (
                                        "tool_request"
                                        if tool_calls
                                        else
                                        "final_response"
                                    ),

                                "tool_calls":
                                    requested_tools,
                            },

                        "duration_ms":
                            duration_ms,
                    }
                ],
            }

        def approval_node(
            state: AgentState,
        ):
            last_message = (
                state[
                    "messages"
                ][-1]
            )

            tool_calls = (
                getattr(
                    last_message,
                    "tool_calls",
                    None,
                )
                or []
            )

            approval_calls = [
                {
                    "name":
                        tool_call.get(
                            "name",
                        ),

                    "args":
                        tool_call.get(
                            "args",
                            {},
                        ),

                    "tool_call_id":
                        tool_call.get(
                            "id",
                        ),

                    "risk_level":
                        risk_by_tool_name.get(
                            tool_call.get(
                                "name",
                                "",
                            ),
                            "READ",
                        ),

                    "execution_policy":
                        ToolExecutionPolicy
                        .HUMAN_APPROVAL
                        .value,
                }
                for tool_call
                in tool_calls
                if (
                    policy_by_tool_name.get(
                        tool_call.get(
                            "name",
                            "",
                        ),
                        ToolExecutionPolicy.AUTO,
                    )
                    ==
                    ToolExecutionPolicy
                    .HUMAN_APPROVAL
                )
            ]

            if not approval_calls:
                return {
                    "approval":
                        None,
                }

            decision = interrupt(
                {
                    "type":
                        "tool_approval",

                    "message":
                        (
                            "One or more tools "
                            "require human approval."
                        ),

                    "tools":
                        approval_calls,
                }
            )

            return {
                "approval":
                    decision,
            }

        async def execute_tools(
            state: AgentState,
        ):
            if (
                langgraph_tool_node
                is None
            ):
                return {}

            last_message = (
                state[
                    "messages"
                ][-1]
            )

            tool_calls = (
                getattr(
                    last_message,
                    "tool_calls",
                    None,
                )
                or []
            )

            requested_tools = [
                {
                    "name":
                        tool_call.get(
                            "name",
                        ),

                    "args":
                        tool_call.get(
                            "args",
                            {},
                        ),
                }
                for tool_call
                in tool_calls
            ]

            for tool_call in (
                requested_tools
            ):
                await self._emit(
                    progress_callback,
                    {
                        "type":
                            "tool_started",

                        "name":
                            tool_call.get(
                                "name"
                            ),

                        "args":
                            tool_call.get(
                                "args",
                                {},
                            ),
                    },
                )

            started_at = (
                time.perf_counter()
            )

            result = (
                await
                langgraph_tool_node
                .ainvoke(
                    state,
                )
            )

            duration_ms = (
                (
                    time.perf_counter()
                    - started_at
                )
                * 1000
            )

            output_messages = (
                result.get(
                    "messages",
                    [],
                )
            )

            outputs = []

            for message in (
                output_messages
            ):
                outputs.append(
                    {
                        "name":
                            getattr(
                                message,
                                "name",
                                None,
                            ),

                        "content":
                            self._safe_output(
                                getattr(
                                    message,
                                    "content",
                                    "",
                                )
                            ),
                    }
                )

            return {
                "messages":
                    output_messages,

                "approval":
                    None,

                "trace": [
                    {
                        "step_type":
                            "TOOL",

                        "name":
                            (
                                requested_tools[
                                    0
                                ][
                                    "name"
                                ]
                                if len(
                                    requested_tools
                                ) == 1
                                else
                                "tools"
                            ),

                        "status":
                            "COMPLETED",

                        "input":
                            {
                                "tool_calls":
                                    requested_tools,
                            },

                        "output":
                            {
                                "results":
                                    outputs,
                            },

                        "duration_ms":
                            duration_ms,
                    }
                ],
            }

        def reject_tools(
            state: AgentState,
        ):
            last_message = (
                state[
                    "messages"
                ][-1]
            )

            tool_calls = (
                getattr(
                    last_message,
                    "tool_calls",
                    None,
                )
                or []
            )

            approval = (
                state.get(
                    "approval"
                )
                or {}
            )

            reason = (
                approval.get(
                    "reason"
                )
                or (
                    "The requested action "
                    "was rejected by a human "
                    "reviewer."
                )
            )

            messages = [
                ToolMessage(
                    content=json.dumps(
                        {
                            "status":
                                "rejected",

                            "reason":
                                reason,
                        }
                    ),
                    tool_call_id=
                        tool_call.get(
                            "id",
                            "",
                        ),
                    name=
                        tool_call.get(
                            "name",
                        ),
                )
                for tool_call
                in tool_calls
            ]

            return {
                "messages":
                    messages,

                "approval":
                    None,

                "trace": [
                    {
                        "step_type":
                            "TOOL",

                        "name":
                            "human_rejected_tools",

                        "status":
                            "COMPLETED",

                        "input":
                            {
                                "tool_calls":
                                    [
                                        {
                                            "name":
                                                item.get(
                                                    "name"
                                                ),

                                            "args":
                                                item.get(
                                                    "args",
                                                    {},
                                                ),
                                        }
                                        for item
                                        in tool_calls
                                    ],
                            },

                        "output":
                            {
                                "decision":
                                    "reject",

                                "reason":
                                    reason,
                            },
                    }
                ],
            }

        def should_continue(
            state: AgentState,
        ):
            if (
                state.get(
                    "llm_calls",
                    0,
                )
                >= max_iterations
            ):
                return END

            messages = (
                state[
                    "messages"
                ]
            )

            if not messages:
                return END

            last_message = (
                messages[-1]
            )

            if (
                getattr(
                    last_message,
                    "tool_calls",
                    None,
                )
            ):
                return "approval"

            return END

        def after_approval(
            state: AgentState,
        ):
            approval = (
                state.get(
                    "approval"
                )
                or {}
            )

            if (
                approval.get(
                    "decision"
                )
                == "reject"
            ):
                return "rejected"

            return "tools"

        graph_builder = (
            StateGraph(
                AgentState,
            )
        )

        graph_builder.add_node(
            "agent",
            call_model,
        )

        graph_builder.add_node(
            "approval",
            approval_node,
        )

        graph_builder.add_node(
            "rejected",
            reject_tools,
        )

        if tools:
            graph_builder.add_node(
                "tools",
                execute_tools,
            )

        graph_builder.add_edge(
            START,
            "agent",
        )

        graph_builder.add_conditional_edges(
            "agent",
            should_continue,
            {
                "approval":
                    "approval",

                END:
                    END,
            },
        )

        if tools:
            graph_builder.add_conditional_edges(
                "approval",
                after_approval,
                {
                    "tools":
                        "tools",

                    "rejected":
                        "rejected",
                },
            )

            graph_builder.add_edge(
                "tools",
                "agent",
            )
        else:
            graph_builder.add_edge(
                "approval",
                END,
            )

        graph_builder.add_edge(
            "rejected",
            "agent",
        )

        return graph_builder.compile(
            checkpointer=
                checkpointer,
        )

    @staticmethod
    def _serialize_message(
        message,
    ) -> dict:
        """Return a UI-safe view of a LangChain message."""
        return {
            "type":
                getattr(
                    message,
                    "type",
                    message
                    .__class__
                    .__name__,
                ),

            "id":
                getattr(
                    message,
                    "id",
                    None,
                ),

            "content":
                getattr(
                    message,
                    "content",
                    None,
                ),

            "name":
                getattr(
                    message,
                    "name",
                    None,
                ),

            "tool_calls":
                getattr(
                    message,
                    "tool_calls",
                    None,
                ),

            "tool_call_id":
                getattr(
                    message,
                    "tool_call_id",
                    None,
                ),
        }

    def _serialize_snapshot(
        self,
        snapshot,
    ) -> dict:
        values = (
            getattr(
                snapshot,
                "values",
                {},
            )
            or {}
        )

        messages = (
            values.get(
                "messages",
                [],
            )
            or []
        )

        return {
            "checkpoint_id":
                self._checkpoint_id(
                    snapshot
                ),

            "next":
                list(
                    getattr(
                        snapshot,
                        "next",
                        (),
                    )
                    or ()
                ),

            "created_at":
                getattr(
                    snapshot,
                    "created_at",
                    None,
                ),

            "metadata":
                getattr(
                    snapshot,
                    "metadata",
                    {},
                )
                or {},

            "interrupts":
                self._interrupt_payloads(
                    snapshot
                ),

            "state":
                {
                    "messages":
                        [
                            self._serialize_message(
                                message
                            )
                            for message
                            in messages
                        ],

                    "message_count":
                        len(
                            messages
                        ),

                    "llm_calls":
                        int(
                            values.get(
                                "llm_calls",
                                0,
                            )
                            or 0
                        ),

                    "active_run_id":
                        values.get(
                            "active_run_id"
                        ),

                    "approval":
                        values.get(
                            "approval"
                        ),

                    "trace_count":
                        len(
                            values.get(
                                "trace",
                                [],
                            )
                            or []
                        ),
                },
        }

    async def inspect_state(
        self,
        *,
        model,
        tools: list[BaseTool],
        system_prompt: str,
        max_iterations: int,
        checkpointer,
        thread_id: str,
    ) -> dict:
        """
        Read the current durable state through LangGraph's public graph API.
        Knowgentiq does not query checkpoint tables directly.
        """
        graph = await self._build_graph(
            model=
                model,
            tools=
                tools,
            system_prompt=
                system_prompt,
            max_iterations=
                max_iterations,
            checkpointer=
                checkpointer,
            progress_callback=
                None,
        )

        config = {
            "configurable": {
                "thread_id":
                    thread_id,
            }
        }

        snapshot = (
            await graph.aget_state(
                config
            )
        )

        return (
            self._serialize_snapshot(
                snapshot
            )
        )

    async def checkpoint_history(
        self,
        *,
        model,
        tools: list[BaseTool],
        system_prompt: str,
        max_iterations: int,
        checkpointer,
        thread_id: str,
        limit: int = 20,
    ) -> list[dict]:
        """
        Read checkpoint history through LangGraph get_state_history.
        This is intentionally framework-owned time-travel state.
        """
        graph = await self._build_graph(
            model=
                model,
            tools=
                tools,
            system_prompt=
                system_prompt,
            max_iterations=
                max_iterations,
            checkpointer=
                checkpointer,
            progress_callback=
                None,
        )

        config = {
            "configurable": {
                "thread_id":
                    thread_id,
            }
        }

        history: list[dict] = []

        async for snapshot in (
            graph.aget_state_history(
                config,
                limit=
                    limit,
            )
        ):
            history.append(
                self._serialize_snapshot(
                    snapshot
                )
            )

        return history

    async def run_turn(
        self,
        *,
        model,
        tools: list[BaseTool],
        system_prompt: str,
        query: str,
        max_iterations: int,
        checkpointer,
        thread_id: str,
        run_id: str,
        auto_execute_tool_names:
            set[str] | None = None,
        progress_callback:
            ProgressCallback | None = None,
    ) -> dict:
        graph = await self._build_graph(
            model=
                model,
            tools=
                tools,
            system_prompt=
                system_prompt,
            max_iterations=
                max_iterations,
            checkpointer=
                checkpointer,
            progress_callback=
                progress_callback,
            auto_execute_tool_names=
                auto_execute_tool_names,
        )

        config = {
            "configurable": {
                "thread_id":
                    thread_id,
            }
        }

        before = (
            await graph.aget_state(
                config
            )
        )

        pending_interrupts = (
            self._interrupt_payloads(
                before
            )
        )

        if pending_interrupts:
            raise RuntimeError(
                "This agent thread is waiting "
                "for human approval and must "
                "be resumed before a new user "
                "message is accepted."
            )

        before_values = (
            getattr(
                before,
                "values",
                {},
            )
            or {}
        )

        message_offset = len(
            before_values.get(
                "messages",
                [],
            )
        )

        trace_offset = len(
            before_values.get(
                "trace",
                [],
            )
        )

        result = await graph.ainvoke(
            {
                "messages": [
                    HumanMessage(
                        content=
                            query,
                    )
                ],

                "llm_calls":
                    0,

                "trace":
                    [],

                "active_run_id":
                    run_id,

                "approval":
                    None,
            },
            config=
                config,
        )

        return await self._result(
            graph=
                graph,
            config=
                config,
            result=
                result,
            message_offset=
                message_offset,
            trace_offset=
                trace_offset,
            llm_calls_before=
                0,
        )

    async def resume(
        self,
        *,
        model,
        tools: list[BaseTool],
        system_prompt: str,
        max_iterations: int,
        checkpointer,
        thread_id: str,
        decision: dict,
        progress_callback:
            ProgressCallback | None = None,
    ) -> dict:
        graph = await self._build_graph(
            model=
                model,
            tools=
                tools,
            system_prompt=
                system_prompt,
            max_iterations=
                max_iterations,
            checkpointer=
                checkpointer,
            progress_callback=
                progress_callback,
        )

        config = {
            "configurable": {
                "thread_id":
                    thread_id,
            }
        }

        before = (
            await graph.aget_state(
                config
            )
        )

        interrupts = (
            self._interrupt_payloads(
                before
            )
        )

        if not interrupts:
            raise RuntimeError(
                "This agent thread has no "
                "pending human approval."
            )

        before_values = (
            getattr(
                before,
                "values",
                {},
            )
            or {}
        )

        message_offset = len(
            before_values.get(
                "messages",
                [],
            )
        )

        trace_offset = len(
            before_values.get(
                "trace",
                [],
            )
        )

        llm_calls_before = int(
            before_values.get(
                "llm_calls",
                0,
            )
            or 0
        )

        result = await graph.ainvoke(
            Command(
                resume=
                    decision,
            ),
            config=
                config,
        )

        return await self._result(
            graph=
                graph,
            config=
                config,
            result=
                result,
            message_offset=
                message_offset,
            trace_offset=
                trace_offset,
            llm_calls_before=
                llm_calls_before,
        )

    async def _result(
        self,
        *,
        graph,
        config: dict,
        result: dict,
        message_offset: int,
        trace_offset: int,
        llm_calls_before: int,
    ) -> dict:
        snapshot = (
            await graph.aget_state(
                config
            )
        )

        interrupts = (
            self._interrupt_payloads(
                snapshot
            )
        )

        messages = (
            result.get(
                "messages",
                [],
            )
            or []
        )

        trace = (
            result.get(
                "trace",
                [],
            )
            or []
        )

        new_messages = (
            messages[
                message_offset:
            ]
        )

        new_trace = (
            trace[
                trace_offset:
            ]
        )

        total_llm_calls = int(
            result.get(
                "llm_calls",
                llm_calls_before,
            )
            or 0
        )

        answer = None

        if not interrupts:
            for message in reversed(
                messages
            ):
                if isinstance(
                    message,
                    AIMessage,
                ):
                    content = (
                        getattr(
                            message,
                            "content",
                            "",
                        )
                    )

                    answer = (
                        content
                        if isinstance(
                            content,
                            str,
                        )
                        else str(
                            content
                        )
                    )

                    break

        return {
            "answer":
                answer,

            "interrupted":
                bool(
                    interrupts
                ),

            "interrupts":
                interrupts,

            "checkpoint_id":
                self._checkpoint_id(
                    snapshot
                ),

            "llm_calls":
                total_llm_calls,

            "llm_calls_delta":
                max(
                    0,
                    total_llm_calls
                    - llm_calls_before,
                ),

            "messages":
                messages,

            "new_messages":
                new_messages,

            "trace":
                new_trace,
        }
