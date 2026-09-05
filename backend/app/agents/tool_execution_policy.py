from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ToolExecutionPolicy(
    str,
    Enum,
):
    AUTO = "AUTO"
    HUMAN_APPROVAL = (
        "HUMAN_APPROVAL"
    )


@dataclass(
    frozen=True,
)
class ToolExecutionPolicyContext:
    """
    Execution-policy inputs supplied by the invocation context.

    Risk classification and execution policy are intentionally
    separate concerns:

    - risk_level describes what the tool can do
    - this context describes what the current invocation allows

    For the current MVP, public channels supply a set of WRITE
    tool names that are explicitly allowed to auto-execute.
    """

    auto_execute_tool_names: (
        frozenset[str]
    ) = frozenset()

    @classmethod
    def from_auto_execute_tool_names(
        cls,
        names: set[str] | None,
    ) -> "ToolExecutionPolicyContext":
        normalized = frozenset(
            str(name).strip()
            for name in (
                names
                or set()
            )
            if str(name).strip()
        )

        return cls(
            auto_execute_tool_names=
                normalized,
        )


class ToolExecutionPolicyResolver:
    """
    Resolve deterministic execution policy for one tool call.

    The LLM never decides this policy.

    Current MVP behavior is preserved:
    - READ tools execute automatically.
    - WRITE tools explicitly allowed by the invocation context
      execute automatically.
    - Other WRITE tools require human approval.

    Future policy sources can be added here without changing the
    LangGraph approval node: tenant policy, agent policy, channel
    policy, user role, environment, tool-level policy, etc.
    """

    def resolve(
        self,
        *,
        tool_name: str,
        risk_level: str,
        context:
            ToolExecutionPolicyContext
            | None = None,
    ) -> ToolExecutionPolicy:
        normalized_name = (
            str(tool_name)
            .strip()
        )

        normalized_risk = (
            str(risk_level)
            .strip()
            .upper()
        )

        resolved_context = (
            context
            or
            ToolExecutionPolicyContext()
        )

        if (
            normalized_risk
            != "WRITE"
        ):
            return (
                ToolExecutionPolicy.AUTO
            )

        if (
            normalized_name
            in resolved_context
            .auto_execute_tool_names
        ):
            return (
                ToolExecutionPolicy.AUTO
            )

        return (
            ToolExecutionPolicy
            .HUMAN_APPROVAL
        )
