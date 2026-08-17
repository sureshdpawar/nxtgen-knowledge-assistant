from __future__ import annotations

import logging
import re

from typing import Any

import httpx

from langchain_core.tools import (
    BaseTool,
    StructuredTool,
)
from pydantic import (
    BaseModel,
    create_model,
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
    "nxtgen.rest_tool"
)


class RESTToolFactory:

    def _python_type(
        self,
        schema: dict,
    ) -> type:
        schema_type = schema.get(
            "type",
            "string",
        )

        if schema_type == "integer":
            return int

        if schema_type == "number":
            return float

        if schema_type == "boolean":
            return bool

        if schema_type == "array":
            return list

        if schema_type == "object":
            return dict

        return str

    def _create_args_schema(
        self,
        tool: ToolDefinition,
    ) -> type[BaseModel]:
        schema = (
            tool.input_schema
            or {}
        )

        properties = schema.get(
            "properties",
            {},
        )

        required = set(
            schema.get(
                "required",
                [],
            )
        )

        fields = {}

        for (
            field_name,
            field_schema,
        ) in properties.items():
            field_type = (
                self._python_type(
                    field_schema,
                )
            )

            if (
                field_name
                in required
            ):
                fields[
                    field_name
                ] = (
                    field_type,
                    ...,
                )
            else:
                fields[
                    field_name
                ] = (
                    field_type | None,
                    None,
                )

        model_name = (
            f"{tool.name}Input"
        )

        return create_model(
            model_name,
            **fields,
        )

    def _build_headers(
        self,
        integration: Integration,
    ) -> dict[str, str]:
        headers = {
            "Accept":
                "application/json",
        }

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

    def _parse_response_body(
        self,
        response: httpx.Response,
    ) -> Any:
        content_type = (
            response.headers.get(
                "content-type",
                "",
            )
        )

        if (
            "application/json"
            in content_type.lower()
        ):
            try:
                return response.json()
            except Exception:
                pass

        return {
            "text":
                response.text,
        }

    def _build_business_error(
        self,
        *,
        tool: ToolDefinition,
        response: httpx.Response,
    ) -> dict:
        body = (
            self._parse_response_body(
                response,
            )
        )

        message = None

        if isinstance(
            body,
            dict,
        ):
            message = (
                body.get(
                    "detail",
                )
                or body.get(
                    "message",
                )
                or body.get(
                    "error",
                )
            )

        if not message:
            message = (
                "The requested resource "
                "could not be found."
            )

        return {
            "tool":
                tool.name,

            "success":
                False,

            "status_code":
                response.status_code,

            "error":
                "RESOURCE_NOT_FOUND",

            "message":
                str(
                    message
                ),

            "result":
                body,
        }

    def _execute(
        self,
        *,
        tool: ToolDefinition,
        integration: Integration,
        arguments: dict[
            str,
            Any,
        ],
    ) -> dict:
        configuration = (
            tool.configuration
            or {}
        )

        method = str(
            configuration.get(
                "method",
                "GET",
            )
        ).upper()

        path = str(
            configuration.get(
                "path",
                "",
            )
        )

        if not path:
            raise ValueError(
                "REST tool configuration "
                "must contain 'path'."
            )

        logger.info(
            "REST tool arguments "
            "tool=%s "
            "arguments=%s",
            tool.name,
            arguments,
        )

        path_parameter_names = set(
            re.findall(
                r"\{([^{}]+)\}",
                path,
            )
        )

        missing_path_parameters = [
            parameter_name
            for parameter_name
            in path_parameter_names
            if (
                parameter_name
                not in arguments
                or arguments[
                    parameter_name
                ] is None
            )
        ]

        if missing_path_parameters:
            raise ValueError(
                "REST tool is missing "
                "required path parameters: "
                + ", ".join(
                    missing_path_parameters
                )
            )

        for parameter_name in (
            path_parameter_names
        ):
            path = path.replace(
                (
                    "{"
                    + parameter_name
                    + "}"
                ),
                str(
                    arguments[
                        parameter_name
                    ]
                ),
            )

        remaining_arguments = {
            key: value
            for (
                key,
                value,
            ) in arguments.items()
            if (
                key
                not in path_parameter_names
                and value is not None
            )
        }

        base_url = (
            integration
            .base_url
            .rstrip("/")
        )

        normalized_path = (
            path.lstrip("/")
        )

        url = (
            f"{base_url}/"
            f"{normalized_path}"
        )

        headers = (
            self._build_headers(
                integration,
            )
        )

        timeout_seconds = float(
            configuration.get(
                "timeout_seconds",
                15,
            )
        )

        logger.info(
            "REST tool invocation "
            "tool=%s "
            "integration=%s "
            "method=%s "
            "url=%s",
            tool.name,
            integration.id,
            method,
            url,
        )

        request_kwargs: dict[
            str,
            Any,
        ] = {
            "headers":
                headers,

            "timeout":
                timeout_seconds,
        }

        if method in {
            "GET",
            "DELETE",
        }:
            request_kwargs[
                "params"
            ] = (
                remaining_arguments
            )
        else:
            request_kwargs[
                "json"
            ] = (
                remaining_arguments
            )

        try:
            with httpx.Client() as client:
                response = (
                    client.request(
                        method,
                        url,
                        **request_kwargs,
                    )
                )

        except httpx.TimeoutException as exc:
            logger.exception(
                "REST tool timeout "
                "tool=%s "
                "url=%s",
                tool.name,
                url,
            )

            return {
                "tool":
                    tool.name,

                "success":
                    False,

                "status_code":
                    None,

                "error":
                    "TIMEOUT",

                "message":
                    (
                        "The external service "
                        "did not respond in time."
                    ),
            }

        except httpx.RequestError as exc:
            logger.exception(
                "REST tool connection failure "
                "tool=%s "
                "url=%s "
                "error=%s",
                tool.name,
                url,
                str(
                    exc
                ),
            )

            return {
                "tool":
                    tool.name,

                "success":
                    False,

                "status_code":
                    None,

                "error":
                    "CONNECTION_ERROR",

                "message":
                    (
                        "The external service "
                        "could not be reached."
                    ),
            }

        #
        # 404 is a valid business outcome.
        # Do not fail the entire Agent run.
        #
        if (
            response.status_code
            == 404
        ):
            logger.info(
                "REST tool resource not found "
                "tool=%s "
                "url=%s",
                tool.name,
                url,
            )

            return (
                self._build_business_error(
                    tool=tool,
                    response=
                        response,
                )
            )

        #
        # 400 / 422 usually means the
        # tool input was rejected by
        # the external API. Return this
        # to the LLM so it can respond
        # or potentially retry.
        #
        if response.status_code in {
            400,
            422,
        }:
            body = (
                self._parse_response_body(
                    response,
                )
            )

            logger.warning(
                "REST tool input rejected "
                "tool=%s "
                "status=%s "
                "url=%s",
                tool.name,
                response.status_code,
                url,
            )

            return {
                "tool":
                    tool.name,

                "success":
                    False,

                "status_code":
                    response.status_code,

                "error":
                    "INVALID_REQUEST",

                "message":
                    (
                        "The external service "
                        "rejected the request."
                    ),

                "result":
                    body,
            }

        #
        # Authentication / authorization
        # problems indicate an integration
        # configuration issue.
        #
        if response.status_code in {
            401,
            403,
        }:
            logger.error(
                "REST tool authorization failure "
                "tool=%s "
                "integration=%s "
                "status=%s",
                tool.name,
                integration.id,
                response.status_code,
            )

            return {
                "tool":
                    tool.name,

                "success":
                    False,

                "status_code":
                    response.status_code,

                "error":
                    "AUTHORIZATION_ERROR",

                "message":
                    (
                        "The integration is "
                        "not authorized to "
                        "perform this request."
                    ),
            }

        #
        # Unexpected upstream server errors
        # are returned as structured tool
        # failures rather than crashing
        # LangGraph.
        #
        if (
            response.status_code
            >= 500
        ):
            logger.error(
                "REST tool upstream failure "
                "tool=%s "
                "integration=%s "
                "status=%s "
                "url=%s",
                tool.name,
                integration.id,
                response.status_code,
                url,
            )

            return {
                "tool":
                    tool.name,

                "success":
                    False,

                "status_code":
                    response.status_code,

                "error":
                    "UPSTREAM_ERROR",

                "message":
                    (
                        "The external service "
                        "encountered an error."
                    ),
            }

        #
        # Any other unexpected non-success
        # status is also normalized.
        #
        if (
            response.status_code
            < 200
            or response.status_code
            >= 300
        ):
            body = (
                self._parse_response_body(
                    response,
                )
            )

            logger.warning(
                "REST tool non-success response "
                "tool=%s "
                "status=%s "
                "url=%s",
                tool.name,
                response.status_code,
                url,
            )

            return {
                "tool":
                    tool.name,

                "success":
                    False,

                "status_code":
                    response.status_code,

                "error":
                    "HTTP_ERROR",

                "message":
                    (
                        "The external service "
                        "returned a non-success "
                        "response."
                    ),

                "result":
                    body,
            }

        result = (
            self._parse_response_body(
                response,
            )
        )

        logger.info(
            "REST tool completed "
            "tool=%s "
            "status=%s",
            tool.name,
            response.status_code,
        )

        return {
            "tool":
                tool.name,

            "success":
                True,

            "status_code":
                response.status_code,

            "result":
                result,
        }

    def create(
        self,
        tool: ToolDefinition,
        integration: Integration,
    ) -> BaseTool:
        args_schema = (
            self._create_args_schema(
                tool,
            )
        )

        logger.info(
            "Creating REST tool "
            "tool=%s "
            "input_schema=%s "
            "generated_schema=%s "
            "configuration=%s",
            tool.name,
            tool.input_schema,
            args_schema.model_json_schema(),
            tool.configuration,
        )

        def execute_tool(
            **kwargs,
        ):
            return self._execute(
                tool=tool,
                integration=
                    integration,
                arguments=
                    kwargs,
            )

        return (
            StructuredTool
            .from_function(
                func=
                    execute_tool,

                name=
                    tool.name,

                description=
                    tool.description,

                args_schema=
                    args_schema,

                infer_schema=
                    False,

                metadata={
                    "tool_definition_id":
                        str(
                            tool.id
                        ),

                    "integration_id":
                        str(
                            integration.id
                        ),

                    "tool_type":
                        "REST",

                    "risk_level":
                        tool.risk_level.value,
                },
            )
        )