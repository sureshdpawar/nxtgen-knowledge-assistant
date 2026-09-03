from __future__ import annotations

import logging

from collections import defaultdict
from uuid import UUID

from langchain_core.tools import (
    BaseTool,
)
from sqlalchemy import (
    select,
)
from sqlalchemy.orm import (
    Session,
    selectinload,
)

from app.agents.mcp_tool_provider import (
    MCPToolProvider,
)
from app.agents.rest_tool_factory import (
    RESTToolFactory,
)
from app.agents.tools.knowledge_search import (
    create_knowledge_search_tool,
)
from app.core.enums import (
    ToolRiskLevel,
    ToolType,
)
from app.models.tool_definition import (
    ToolDefinition,
)


logger = logging.getLogger(
    "nxtgen.agent_tools"
)


class AgentToolRegistry:

    def __init__(self):
        self.rest_tool_factory = (
            RESTToolFactory()
        )

        self.mcp_tool_provider = (
            MCPToolProvider()
        )

    def _apply_governance_metadata(
        self,
        tool: BaseTool,
        *,
        risk_level: ToolRiskLevel,
        tool_definition_id:
            UUID | None = None,
    ) -> BaseTool:
        metadata = dict(
            getattr(
                tool,
                "metadata",
                None,
            )
            or {}
        )

        metadata[
            "knowgentiq"
        ] = {
            "risk_level":
                risk_level.value,

            "tool_definition_id":
                (
                    str(
                        tool_definition_id
                    )
                    if tool_definition_id
                    else None
                ),
        }

        tool.metadata = metadata

        return tool

    def _get_assigned_tools(
        self,
        db: Session,
        *,
        tenant_id: UUID,
        tool_ids: list[UUID],
    ) -> list[ToolDefinition]:

        if not tool_ids:
            return []

        stmt = (
            select(
                ToolDefinition,
            )
            .options(
                selectinload(
                    ToolDefinition.integration,
                )
            )
            .where(
                ToolDefinition.id.in_(
                    tool_ids,
                ),

                ToolDefinition.tenant_id
                == tenant_id,

                ToolDefinition.is_active
                .is_(True),
            )
        )

        return list(
            db.scalars(
                stmt,
            ).all()
        )

    async def get_tools(
        self,
        db: Session,
        tenant_id: UUID,
        knowledge_base_ids:
            list[UUID],
        tool_ids:
            list[UUID],
    ) -> list[BaseTool]:

        tools: list[
            BaseTool
        ] = []

        if knowledge_base_ids:
            knowledge_tool = (
                create_knowledge_search_tool(
                    db=db,
                    knowledge_base_ids=
                        knowledge_base_ids,
                )
            )

            tools.append(
                self._apply_governance_metadata(
                    knowledge_tool,
                    risk_level=
                        ToolRiskLevel.READ,
                )
            )

        definitions = (
            self._get_assigned_tools(
                db=db,
                tenant_id=
                    tenant_id,
                tool_ids=
                    tool_ids,
            )
        )

        for definition in definitions:
            if (
                definition.tool_type
                != ToolType.REST
            ):
                continue

            integration = (
                definition.integration
            )

            if (
                integration is None
                or not
                integration.is_active
            ):
                continue

            rest_tool = (
                self.rest_tool_factory
                .create(
                    tool=
                        definition,
                    integration=
                        integration,
                )
            )

            tools.append(
                self._apply_governance_metadata(
                    rest_tool,
                    risk_level=
                        definition.risk_level,
                    tool_definition_id=
                        definition.id,
                )
            )

        mcp_definitions_by_integration: dict[
            UUID,
            list[ToolDefinition],
        ] = defaultdict(
            list,
        )

        for definition in definitions:
            if (
                definition.tool_type
                != ToolType.MCP
            ):
                continue

            integration = (
                definition.integration
            )

            if (
                integration is None
                or not
                integration.is_active
            ):
                continue

            mcp_definitions_by_integration[
                integration.id
            ].append(
                definition,
            )

        for (
            integration_id,
            mcp_definitions,
        ) in (
            mcp_definitions_by_integration
            .items()
        ):
            integration = (
                mcp_definitions[
                    0
                ].integration
            )

            if integration is None:
                continue

            try:
                selected_tools = (
                    await
                    self.mcp_tool_provider
                    .get_assigned_tools(
                        integration=
                            integration,
                        definitions=
                            mcp_definitions,
                    )
                )

                definitions_by_name = {
                    definition.name:
                        definition
                    for definition
                    in mcp_definitions
                }

                for tool in selected_tools:
                    definition = (
                        definitions_by_name.get(
                            tool.name
                        )
                    )

                    if definition is None:
                        continue

                    tools.append(
                        self._apply_governance_metadata(
                            tool,
                            risk_level=
                                definition.risk_level,
                            tool_definition_id=
                                definition.id,
                        )
                    )

            except Exception:
                logger.exception(
                    "MCP tool discovery failed "
                    "integration=%s",
                    integration_id,
                )

                raise

        logger.info(
            "Agent tools resolved "
            "knowledge_bases=%s "
            "assigned_definitions=%s "
            "runtime_tools=%s",
            len(
                knowledge_base_ids
            ),
            len(
                definitions
            ),
            [
                tool.name
                for tool in tools
            ],
        )

        return tools
