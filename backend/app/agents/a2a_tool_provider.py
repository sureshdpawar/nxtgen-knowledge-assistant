from __future__ import annotations

import json
import re
from uuid import UUID

from langchain_core.tools import (
    BaseTool,
    StructuredTool,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.a2a_context import a2a_delegation_depth
from app.core.enums import AgentStatus
from app.models.agent import Agent
from app.models.agent_a2a_connection import AgentA2AConnection
from app.services.a2a_service import A2AService


class A2AAgentToolProvider:
    def __init__(self):
        self.a2a_service = A2AService()

    def _tool_name(
        self,
        target: Agent,
    ) -> str:
        slug = re.sub(
            r"[^a-z0-9]+",
            "_",
            target.name.lower(),
        ).strip("_")
        slug = slug[:42] or "agent"
        return f"a2a_{slug}_{str(target.id)[:8]}"

    async def get_connected_agent_tools(
        self,
        *,
        db: Session,
        tenant_id: UUID,
        source_agent_id: UUID,
    ) -> list[BaseTool]:
        # Deliberately one-hop for the interview/demo slice.
        if a2a_delegation_depth.get() >= 1:
            return []

        source = db.get(Agent, source_agent_id)
        if (
            source is None
            or source.tenant_id != tenant_id
        ):
            return []

        stmt = (
            select(Agent)
            .join(
                AgentA2AConnection,
                AgentA2AConnection.target_agent_id
                == Agent.id,
            )
            .where(
                AgentA2AConnection.tenant_id == tenant_id,
                AgentA2AConnection.source_agent_id == source_agent_id,
                Agent.status == AgentStatus.ACTIVE,
            )
            .order_by(Agent.name.asc())
        )

        targets = list(db.scalars(stmt).all())
        tools: list[BaseTool] = []

        for target in targets:
            target_id = target.id
            target_name = target.name
            description = (
                str(target.description or "").strip()
                or f"Specialist Knowgentiq agent: {target.name}"
            )

            def make_delegate(
                resolved_target_id: UUID,
            ):
                async def delegate(
                    message: str,
                ) -> str:
                    result = await self.a2a_service.delegate(
                        db=db,
                        tenant_id=tenant_id,
                        source_agent_id=source_agent_id,
                        target_agent_id=resolved_target_id,
                        message=message,
                    )
                    return json.dumps(
                        result,
                        default=str,
                    )

                return delegate

            tool = StructuredTool.from_function(
                coroutine=make_delegate(
                    target_id
                ),
                name=self._tool_name(target),
                description=(
                    f"A2A v1 delegation to '{target_name}'. "
                    f"Use this when the request belongs to this "
                    f"specialist agent. Capability: {description}. "
                    "Pass a clear standalone task/message for the "
                    "specialist. The returned JSON includes the "
                    "child AgentRun id and answer."
                ),
            )

            tool.metadata = {
                "knowgentiq": {
                    "risk_level": "READ",
                    "tool_definition_id": None,
                    "capability_type": "A2A",
                    "protocol": "A2A",
                    "protocol_version": "1.0",
                    "target_agent_id": str(target.id),
                    "target_agent_name": target.name,
                }
            }
            tools.append(tool)

        return tools
