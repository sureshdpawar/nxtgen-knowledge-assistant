from __future__ import annotations

import logging

from langchain_core.tools import (
    BaseTool,
)
from langchain_mcp_adapters.client import (
    MultiServerMCPClient,
)

from app.core.enums import (
    IntegrationAuthType,
)
from app.models.integration import (
    Integration,
)
from app.models.tool_definition import (
    ToolDefinition,
)


logger = logging.getLogger(
    "nxtgen.mcp_tools"
)


class MCPToolProvider:

    def _build_headers(
        self,
        integration: Integration,
    ) -> dict[str, str]:

        headers: dict[
            str,
            str,
        ] = {}

        auth_config = (
            integration.auth_config
            or {}
        )

        if (
            integration.auth_type
            == IntegrationAuthType.BEARER
        ):
            token = auth_config.get(
                "token",
            )

            if token:
                headers[
                    "Authorization"
                ] = (
                    f"Bearer {token}"
                )

        elif (
            integration.auth_type
            == IntegrationAuthType.API_KEY
        ):
            header_name = (
                auth_config.get(
                    "header_name",
                    "X-API-Key",
                )
            )

            value = auth_config.get(
                "value",
            )

            if value:
                headers[
                    str(
                        header_name
                    )
                ] = str(
                    value
                )

        return headers

    async def _load_tools(
        self,
        integration: Integration,
    ) -> list[BaseTool]:

        headers = (
            self._build_headers(
                integration,
            )
        )

        server_name = (
            f"integration_"
            f"{integration.id}"
        )

        connection = {
            "transport":
                "http",

            "url":
                integration.base_url,
        }

        if headers:
            connection[
                "headers"
            ] = headers

        logger.info(
            "Connecting to MCP server "
            "integration=%s "
            "url=%s",
            integration.id,
            integration.base_url,
        )

        client = (
            MultiServerMCPClient(
                {
                    server_name:
                        connection,
                }
            )
        )

        tools = (
            await client.get_tools()
        )

        logger.info(
            "MCP tools discovered "
            "integration=%s "
            "count=%s "
            "tools=%s",
            integration.id,
            len(
                tools
            ),
            [
                tool.name
                for tool in tools
            ],
        )

        return tools

    async def get_assigned_tools(
        self,
        *,
        integration: Integration,
        definitions: list[
            ToolDefinition
        ],
    ) -> list[BaseTool]:

        discovered_tools = (
            await self._load_tools(
                integration,
            )
        )

        allowed_names = {
            definition.name
            for definition
            in definitions
        }

        selected_tools = [
            tool
            for tool
            in discovered_tools
            if (
                tool.name
                in allowed_names
            )
        ]

        logger.info(
            "MCP tools selected "
            "integration=%s "
            "allowed=%s "
            "selected=%s",
            integration.id,
            sorted(
                allowed_names
            ),
            [
                tool.name
                for tool
                in selected_tools
            ],
        )

        return selected_tools