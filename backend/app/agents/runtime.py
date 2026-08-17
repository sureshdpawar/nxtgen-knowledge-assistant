from __future__ import annotations

import inspect
import logging
import time

from collections.abc import (
    Awaitable,
    Callable,
)
from typing import Any

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)
from langchain_core.tools import (
    BaseTool,
)
from langgraph.graph import (
    END,
    START,
    StateGraph,
)
from langgraph.prebuilt import (
    ToolNode,
)

from app.agents.state import (
    AgentState,
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

    async def _emit(
        self,
        callback:
            ProgressCallback | None,
        event: dict[
            str,
            Any,
        ],
    ) -> None:
        if callback is None:
            return

        result = callback(
            event,
        )

        if inspect.isawaitable(
            result,
        ):
            await result

    def _safe_output(
        self,
        value,
    ) -> str:
        text = str(
            value,
        )

        if (
            len(text)
            <= MAX_TRACE_OUTPUT_LENGTH
        ):
            return text

        return (
            text[
                :MAX_TRACE_OUTPUT_LENGTH
            ]
            + "...[truncated]"
        )

    async def run(
        self,
        *,
        model,
        tools: list[
            BaseTool
        ],
        system_prompt: str,
        query: str,
        max_iterations: int,
        progress_callback:
            ProgressCallback | None = None,
    ) -> dict:

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
            model_with_tools = (
                model
            )

            langgraph_tool_node = (
                None
            )

        async def call_model(
            state: AgentState,
        ):
            llm_calls = (
                state.get(
                    "llm_calls",
                    0,
                )
            )

            if (
                llm_calls
                >= max_iterations
            ):
                return {
                    "messages": [],
                    "llm_calls":
                        llm_calls,
                    "trace": [],
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

            logger.info(
                "Agent LLM invocation "
                "iteration=%s "
                "max_iterations=%s",
                iteration,
                max_iterations,
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
                            item[
                                "name"
                            ]
                            for item
                            in requested_tools
                            if item[
                                "name"
                            ]
                        ],
                },
            )

            trace_step = {
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

            return {
                "messages": [
                    response,
                ],

                "llm_calls":
                    iteration,

                "trace": [
                    trace_step,
                ],
            }

        async def execute_tools(
            state: AgentState,
        ):
            if (
                langgraph_tool_node
                is None
            ):
                return {
                    "messages": [],
                    "trace": [],
                }

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

            for tool_call in (
                requested_tools
            ):
                tool_name = (
                    tool_call.get(
                        "name"
                    )
                )

                matching_output = next(
                    (
                        output
                        for output
                        in outputs
                        if (
                            output.get(
                                "name"
                            )
                            == tool_name
                        )
                    ),
                    None,
                )

                await self._emit(
                    progress_callback,
                    {
                        "type":
                            "tool_completed",

                        "name":
                            tool_name,

                        "duration_ms":
                            duration_ms,

                        "output":
                            matching_output,
                    },
                )

            trace_step = {
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

            logger.info(
                "Agent tool execution "
                "tools=%s "
                "duration_ms=%.2f",
                [
                    tool[
                        "name"
                    ]
                    for tool
                    in requested_tools
                ],
                duration_ms,
            )

            return {
                "messages":
                    output_messages,

                "trace": [
                    trace_step,
                ],
            }

        def should_continue(
            state: AgentState,
        ):
            llm_calls = (
                state.get(
                    "llm_calls",
                    0,
                )
            )

            if (
                llm_calls
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

            tool_calls = (
                getattr(
                    last_message,
                    "tool_calls",
                    None,
                )
            )

            if tool_calls:
                return "tools"

            return END

        graph_builder = (
            StateGraph(
                AgentState,
            )
        )

        graph_builder.add_node(
            "agent",
            call_model,
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

        if tools:
            graph_builder.add_conditional_edges(
                "agent",
                should_continue,
                {
                    "tools":
                        "tools",

                    END:
                        END,
                },
            )

            graph_builder.add_edge(
                "tools",
                "agent",
            )

        else:
            graph_builder.add_edge(
                "agent",
                END,
            )

        graph = (
            graph_builder.compile()
        )

        result = (
            await graph.ainvoke(
                {
                    "messages": [
                        HumanMessage(
                            content=
                                query,
                        ),
                    ],

                    "llm_calls":
                        0,

                    "trace":
                        [],
                }
            )
        )

        messages = (
            result.get(
                "messages",
                [],
            )
        )

        answer = ""

        if messages:
            last_message = (
                messages[-1]
            )

            content = (
                getattr(
                    last_message,
                    "content",
                    "",
                )
            )

            if isinstance(
                content,
                str,
            ):
                answer = content

            else:
                answer = str(
                    content,
                )

        if not answer:
            answer = (
                "The agent could not "
                "complete the request "
                "within the configured "
                "execution limit."
            )

        return {
            "answer":
                answer,

            "llm_calls":
                result.get(
                    "llm_calls",
                    0,
                ),

            "messages":
                messages,

            "trace":
                result.get(
                    "trace",
                    [],
                ),
        }