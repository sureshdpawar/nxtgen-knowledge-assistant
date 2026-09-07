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
    Deterministic execution-policy inputs for one invocation.

    Risk classification and execution policy are intentionally
    separate concerns:

    - risk_level describes what the tool can do
    - execution policy describes whether that tool may execute
      automatically or requires human approval

    Explicit policy names are used by authenticated/internal
    Agent executions after AgentTool policy persistence.

    auto_execute_tool_names is also retained for the current
    external-channel compatibility path. Channel policy is
    intentionally not redesigned in this slice.
    """

    auto_execute_tool_names: (
        frozenset[str]
    ) = frozenset()

    human_approval_tool_names: (
        frozenset[str]
    ) = frozenset()

    human_approval_supported: bool = True

    @classmethod
    def from_tool_policy_names(
        cls,
        auto_execute_tool_names:
            set[str] | None,
        human_approval_tool_names:
            set[str] | None = None,
        *,
        human_approval_supported: bool = True,
    ) -> "ToolExecutionPolicyContext":
        auto_names = frozenset(
            str(name).strip()
            for name in (
                auto_execute_tool_names
                or set()
            )
            if str(name).strip()
        )

        approval_names = frozenset(
            str(name).strip()
            for name in (
                human_approval_tool_names
                or set()
            )
            if str(name).strip()
        )

        return cls(
            auto_execute_tool_names=
                auto_names,
            human_approval_tool_names=
                approval_names,
            human_approval_supported=
                human_approval_supported,
        )

    @classmethod
    def from_auto_execute_tool_names(
        cls,
        names: set[str] | None,
        *,
        human_approval_supported: bool = True,
    ) -> "ToolExecutionPolicyContext":
        """
        Backwards-compatible constructor for existing callers.
        """
        return cls.from_tool_policy_names(
            auto_execute_tool_names=
                names,
            human_approval_tool_names=
                None,
            human_approval_supported=
                human_approval_supported,
        )


class ToolExecutionPolicyResolver:
    """
    Resolve deterministic execution policy for one tool call.

    The LLM never decides this policy.

    Resolution order:
    1. explicit HUMAN_APPROVAL assignment
    2. explicit AUTO assignment
    3. legacy MVP fallback:
       - READ -> AUTO
       - WRITE -> HUMAN_APPROVAL

    Checking HUMAN_APPROVAL first is intentionally fail-safe if
    contradictory policy inputs are ever supplied.

    human_approval_supported is an execution capability, not a
    policy override. A HUMAN_APPROVAL action is never converted
    to AUTO merely because the current surface cannot pause.
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
            normalized_name
            in resolved_context
            .human_approval_tool_names
        ):
            return (
                ToolExecutionPolicy
                .HUMAN_APPROVAL
            )

        if (
            normalized_name
            in resolved_context
            .auto_execute_tool_names
        ):
            return (
                ToolExecutionPolicy.AUTO
            )

        if normalized_risk != "WRITE":
            return (
                ToolExecutionPolicy.AUTO
            )

        return (
            ToolExecutionPolicy
            .HUMAN_APPROVAL
        )
