from __future__ import annotations

import logging

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

from app.agents.rest_tool_factory import (
    RESTToolFactory,
)
from app.agents.tools.knowledge_search import (
    create_knowledge_search_tool,
)
from app.core.enums import (
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

    def get_tools(
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

        #
        # Native NXTGEN knowledge tool.
        #
        if knowledge_base_ids:
            tools.append(
                create_knowledge_search_tool(
                    db=db,
                    knowledge_base_ids=
                        knowledge_base_ids,
                )
            )

        #
        # Tenant-configured tools.
        #
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
                == ToolType.REST
            ):
                integration = (
                    definition.integration
                )

                if integration is None:
                    logger.warning(
                        "REST tool skipped "
                        "tool=%s "
                        "reason=no_integration",
                        definition.id,
                    )

                    continue

                if (
                    not
                    integration.is_active
                ):
                    logger.warning(
                        "REST tool skipped "
                        "tool=%s "
                        "integration=%s "
                        "reason=inactive_integration",
                        definition.id,
                        integration.id,
                    )

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
                    rest_tool,
                )

                continue

            if (
                definition.tool_type
                == ToolType.MCP
            ):
                logger.info(
                    "MCP tool skipped "
                    "for now "
                    "tool=%s "
                    "name=%s",
                    definition.id,
                    definition.name,
                )

                continue

            if (
                definition.tool_type
                == ToolType.NATIVE
            ):
                logger.info(
                    "Configured native "
                    "tool skipped "
                    "tool=%s "
                    "name=%s",
                    definition.id,
                    definition.name,
                )

        logger.info(
            "Agent tools resolved "
            "knowledge_bases=%s "
            "assigned_definitions=%s "
            "total_tools=%s "
            "tools=%s",
            len(
                knowledge_base_ids
            ),
            len(
                definitions
            ),
            len(
                tools
            ),
            [
                tool.name
                for tool in tools
            ],
        )

        return tools