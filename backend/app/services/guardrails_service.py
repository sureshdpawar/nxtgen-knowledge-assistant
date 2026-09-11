from __future__ import annotations

from pathlib import Path

from nemoguardrails import (
    Guardrails,
    RailsConfig,
)
from nemoguardrails.rails.llm.options import (
    RailStatus,
    RailType,
)


class GuardrailBlockedError(RuntimeError):
    """Raised when a configured NeMo rail blocks content."""


class GuardrailsService:
    """
    Lightweight NeMo Guardrails adapter.

    Knowgentiq keeps authorization, tenant access,
    tool execution policy, and human approval in
    the existing governance layer. This service
    only applies configured input/output safety
    rails to text crossing the application boundary.
    """

    def __init__(self) -> None:
        config_path = (
            Path(__file__)
            .resolve()
            .parents[2]
            / "guardrails"
        )

        config = (
            RailsConfig.from_path(
                str(config_path)
            )
        )

        self.rails = Guardrails(
            config,
            use_iorails=True,
            require_iorails=True,
        )

    @staticmethod
    def _content_or_original(
        content: str | None,
        original: str,
    ) -> str:
        if content is None:
            return original

        return str(content)

    def check_input(
        self,
        text: str,
    ) -> str:
        result = self.rails.check(
            messages=[
                {
                    "role": "user",
                    "content": text,
                }
            ],
            rail_types=[
                RailType.INPUT,
            ],
        )

        if (
            result.status
            == RailStatus.BLOCKED
        ):
            raise GuardrailBlockedError(
                result.content
                or (
                    "The request was blocked "
                    "by a configured guardrail."
                )
            )

        return self._content_or_original(
            result.content,
            text,
        )

    def check_output(
        self,
        text: str,
    ) -> str:
        if not text:
            return text

        result = self.rails.check(
            messages=[
                {
                    "role": "assistant",
                    "content": text,
                }
            ],
            rail_types=[
                RailType.OUTPUT,
            ],
        )

        if (
            result.status
            == RailStatus.BLOCKED
        ):
            raise GuardrailBlockedError(
                result.content
                or (
                    "The response was blocked "
                    "by a configured guardrail."
                )
            )

        return self._content_or_original(
            result.content,
            text,
        )

    async def check_input_async(
        self,
        text: str,
    ) -> str:
        result = (
            await
            self.rails.check_async(
                messages=[
                    {
                        "role": "user",
                        "content": text,
                    }
                ],
                rail_types=[
                    RailType.INPUT,
                ],
            )
        )

        if (
            result.status
            == RailStatus.BLOCKED
        ):
            raise GuardrailBlockedError(
                result.content
                or (
                    "The request was blocked "
                    "by a configured guardrail."
                )
            )

        return self._content_or_original(
            result.content,
            text,
        )

    async def check_output_async(
        self,
        text: str,
    ) -> str:
        if not text:
            return text

        result = (
            await
            self.rails.check_async(
                messages=[
                    {
                        "role": "assistant",
                        "content": text,
                    }
                ],
                rail_types=[
                    RailType.OUTPUT,
                ],
            )
        )

        if (
            result.status
            == RailStatus.BLOCKED
        ):
            raise GuardrailBlockedError(
                result.content
                or (
                    "The response was blocked "
                    "by a configured guardrail."
                )
            )

        return self._content_or_original(
            result.content,
            text,
        )
