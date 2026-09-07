from __future__ import annotations

import json
import logging
import time

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.agents.tool_registry import AgentToolRegistry
from app.core.enums import AgentStatus
from app.models.chat_channel import ChatChannel
from app.repositories.agent_repository import AgentRepository
from app.services.agent_execution_service import AgentExecutionService


logger = logging.getLogger("nxtgen.website_agent")


class WebsiteAgentService:
    def __init__(self):
        self.agent_repository = AgentRepository()
        self.tool_registry = AgentToolRegistry()
        self.agent_execution_service = AgentExecutionService()

    def execution_mode(self, channel: ChatChannel) -> str:
        value = str(
            (channel.configuration or {}).get(
                "execution_mode",
                "KNOWLEDGE",
            )
        ).strip().upper()

        if value not in {"KNOWLEDGE", "AGENT"}:
            return "KNOWLEDGE"

        return value

    def get_agent(self, db: Session, channel: ChatChannel):
        raw_agent_id = (
            (channel.configuration or {}).get("agent_id")
        )

        if not raw_agent_id:
            raise ValueError("Website agent is not configured.")

        try:
            agent_id = UUID(str(raw_agent_id))
        except ValueError as exc:
            raise ValueError(
                "Website agent configuration is invalid."
            ) from exc

        agent = (
            self.agent_repository
            .get_by_id_and_tenant(
                db=db,
                tenant_id=channel.tenant_id,
                agent_id=agent_id,
            )
        )

        if (
            agent is None
            or agent.status != AgentStatus.ACTIVE
        ):
            raise ValueError(
                "Configured website agent is missing or inactive."
            )

        return agent

    def public_pre_chat_config(
        self,
        channel: ChatChannel,
    ) -> dict:
        raw = (
            (channel.configuration or {}).get("pre_chat", {})
            or {}
        )

        if not isinstance(raw, dict):
            raw = {}

        fields = []

        for item in raw.get("fields", []) or []:
            if not isinstance(item, dict):
                continue

            name = str(item.get("name", "")).strip()
            if not name:
                continue

            input_type = str(
                item.get("input_type", "text")
            ).strip().lower()

            if input_type not in {"text", "tel", "email"}:
                input_type = "text"

            fields.append(
                {
                    "name": name,
                    "label": (
                        str(item.get("label", name)).strip()
                        or name
                    ),
                    "required": bool(
                        item.get("required", False)
                    ),
                    "input_type": input_type,
                    "placeholder": (
                        str(item.get("placeholder"))
                        if item.get("placeholder")
                        else None
                    ),
                }
            )

        return {
            "enabled": bool(raw.get("enabled", False)),
            "title": str(
                raw.get("title", "Before we start")
            ),
            "submit_label": str(
                raw.get("submit_label", "Start chat")
            ),
            "fields": fields,
        }

    def validate_visitor(
        self,
        channel: ChatChannel,
        visitor: dict[str, str],
    ) -> dict[str, str]:
        normalized = {
            str(key).strip(): str(value).strip()
            for key, value in visitor.items()
            if str(key).strip()
        }

        if len(normalized) > 20:
            raise ValueError("Too many pre-chat fields.")

        for value in normalized.values():
            if len(value) > 500:
                raise ValueError(
                    "A pre-chat field is too long."
                )

        pre_chat = self.public_pre_chat_config(channel)

        if not pre_chat["enabled"]:
            return normalized

        configured_names = {
            item["name"]
            for item in pre_chat["fields"]
        }

        normalized = {
            key: value
            for key, value in normalized.items()
            if key in configured_names
        }

        for item in pre_chat["fields"]:
            if (
                item["required"]
                and not normalized.get(item["name"], "")
            ):
                raise ValueError(
                    f"{item['label']} is required."
                )

        return normalized

    async def start_session(
        self,
        db: Session,
        *,
        channel: ChatChannel,
        visitor: dict[str, str],
    ) -> dict:
        agent = self.get_agent(db, channel)
        visitor = self.validate_visitor(
            channel,
            visitor,
        )

        action = (
            (channel.configuration or {})
            .get("session_start_action", {})
            or {}
        )

        if not isinstance(action, dict):
            raise ValueError(
                "Website session-start action "
                "configuration is invalid."
            )

        tool_name = str(
            action.get("tool_name", "")
        ).strip()

        if not tool_name:
            return {}

        arguments = self._build_arguments(
            action.get("arguments", {}),
            visitor,
        )

        tools = await self.tool_registry.get_tools(
            db=db,
            tenant_id=agent.tenant_id,
            knowledge_base_ids=[],
            tool_ids=[
                link.tool_id
                for link in agent.tool_links
            ],
        )

        tool = next(
            (
                item
                for item in tools
                if item.name == tool_name
            ),
            None,
        )

        if tool is None:
            raise ValueError(
                f"Configured session-start tool "
                f"'{tool_name}' is not assigned "
                "to the website agent."
            )

        started_at = time.perf_counter()

        logger.info(
            "Website session-start tool started "
            "channel=%s agent=%s tool=%s",
            channel.id,
            agent.id,
            tool_name,
        )

        result = await tool.ainvoke(arguments)
        normalized_result = (
            self._normalize_tool_result(result)
        )

        if (
            isinstance(normalized_result, dict)
            and normalized_result.get("success") is False
        ):
            raise ValueError(
                str(
                    normalized_result.get(
                        "message",
                        "Session-start action failed.",
                    )
                )
            )

        context = self._extract_context(
            action.get("context", {}),
            normalized_result,
        )

        logger.info(
            "Website session-start tool completed "
            "channel=%s agent=%s tool=%s "
            "duration_ms=%.2f context_keys=%s",
            channel.id,
            agent.id,
            tool_name,
            (
                time.perf_counter()
                - started_at
            )
            * 1000,
            sorted(context.keys()),
        )

        return context

    async def chat(
        self,
        db: Session,
        *,
        channel: ChatChannel,
        visitor_id: str,
        thread_id: UUID,
        runtime_context: dict,
        query: str,
    ) -> dict:
        agent = self.get_agent(db, channel)

        auto_execute = {
            str(name).strip()
            for name in (
                (channel.configuration or {})
                .get("auto_execute_tools", [])
                or []
            )
            if str(name).strip()
        }

        model_context = {
            str(key): value
            for key, value in (
                runtime_context
                or {}
            ).items()
            if isinstance(
                value,
                (str, int, float, bool),
            )
        }

        result = await (
            self.agent_execution_service
            .run_external(
                db=db,
                tenant_id=channel.tenant_id,
                agent_id=agent.id,
                query=query,
                actor_type="WEBSITE_VISITOR",
                actor_id=visitor_id,
                thread_id=thread_id,
                runtime_context=model_context,
                context_metadata={
                    "source": "website",
                    "channel_id": str(channel.id),
                    "visitor_id": visitor_id,
                    "business_context": model_context,
                },
                auto_execute_tool_names=auto_execute,
            )
        )

        if (
            result["status"].value
            == "WAITING_FOR_APPROVAL"
        ):
            raise ValueError(
                "The requested website action "
                "requires an approval policy "
                "that is not enabled for this "
                "public channel."
            )

        return result

    def _build_arguments(
        self,
        raw_mapping: Any,
        visitor: dict[str, str],
    ) -> dict:
        if not isinstance(raw_mapping, dict):
            raise ValueError(
                "Session-start argument mapping "
                "is invalid."
            )

        class VisitorMap(dict):
            def __missing__(self, key):
                return ""

        format_values = VisitorMap(visitor)
        values = {}

        for argument_name, rule in raw_mapping.items():
            argument_name = str(argument_name).strip()

            if not argument_name:
                continue

            omit_if_empty = False

            if isinstance(rule, str):
                value = visitor.get(rule, "")

            elif isinstance(rule, dict):
                omit_if_empty = bool(
                    rule.get("omit_if_empty", False)
                )

                if "template" in rule:
                    value = str(
                        rule.get("template", "")
                    ).format_map(
                        format_values
                    ).strip()
                else:
                    field_name = str(
                        rule.get("field", "")
                    ).strip()

                    value = visitor.get(
                        field_name,
                        "",
                    )
            else:
                continue

            if (
                omit_if_empty
                and (
                    value is None
                    or str(value).strip() == ""
                )
            ):
                continue

            values[argument_name] = value

        return values

    def _normalize_tool_result(
        self,
        value: Any,
    ) -> Any:
        if value is None:
            return None

        if isinstance(value, dict):
            if isinstance(
                value.get("structuredContent"),
                dict,
            ):
                return value["structuredContent"]

            if isinstance(
                value.get("structured_content"),
                dict,
            ):
                return value["structured_content"]

            return value

        if isinstance(value, str):
            text = value.strip()

            try:
                return json.loads(text)
            except Exception:
                return text

        if isinstance(value, list):
            normalized = [
                self._normalize_tool_result(item)
                for item in value
            ]

            if (
                len(normalized) == 1
                and isinstance(normalized[0], dict)
                and "text" in normalized[0]
            ):
                return self._normalize_tool_result(
                    normalized[0]["text"]
                )

            return normalized

        content = getattr(value, "content", None)

        if content is not None:
            return self._normalize_tool_result(content)

        text = getattr(value, "text", None)

        if text is not None:
            return self._normalize_tool_result(text)

        if hasattr(value, "model_dump"):
            return self._normalize_tool_result(
                value.model_dump()
            )

        return value

    def _extract_context(
        self,
        raw_mapping: Any,
        tool_result: Any,
    ) -> dict:
        if not isinstance(raw_mapping, dict):
            return {}

        if not isinstance(tool_result, dict):
            raise ValueError(
                "Session-start tool did not "
                "return structured data."
            )

        context = {}

        for context_key, result_key in raw_mapping.items():
            context_key = str(context_key).strip()
            result_key = str(result_key).strip()

            if not context_key or not result_key:
                continue

            value = tool_result.get(result_key)

            if value is None:
                raise ValueError(
                    f"Session-start tool result "
                    f"did not contain '{result_key}'."
                )

            if not isinstance(
                value,
                (str, int, float, bool),
            ):
                raise ValueError(
                    f"Session context '{context_key}' "
                    "must be a scalar value."
                )

            context[context_key] = value

        return context
