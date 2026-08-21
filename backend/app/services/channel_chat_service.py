import json
import logging
import time

from collections.abc import Generator
from uuid import UUID

from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
)
from sqlalchemy.orm import Session

from app.exceptions.llm import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
)
from app.services.chat_service import ChatService


logger = logging.getLogger(
    "nxtgen.channel_chat"
)


class ChannelChatService(
    ChatService
):
    """
    Chat execution for external ChatChannels.

    Reuses the existing ChatService dependencies:
    - retrieval
    - prompt building
    - LLM factory
    - citation building
    - SSE error helpers

    Conversation ownership differs:
    internal UI -> user_id
    external channel -> chat_channel_id
    """

    def chat(
        self,
        db: Session,
        tenant_id: UUID,
        chat_channel_id: UUID,
        knowledge_base_id: UUID,
        session_id: UUID | None,
        query: str,
    ) -> dict:
        conversation = (
            self.conversation_service
            .get_or_create_channel_conversation(
                db=db,
                tenant_id=tenant_id,
                chat_channel_id=chat_channel_id,
                knowledge_base_id=knowledge_base_id,
                conversation_id=session_id,
                title=query,
            )
        )

        self.conversation_service.save_user_message(
            db=db,
            conversation_id=conversation.id,
            content=query,
        )

        history = (
            self.conversation_service
            .get_messages(
                db=db,
                conversation_id=conversation.id,
            )
        )

        search_results = (
            self.search_service.search(
                db=db,
                knowledge_base_id=knowledge_base_id,
                query=query,
            )
        )

        contexts = [
            chunk.text
            for (
                chunk,
                document,
                knowledge_source,
                similarity,
            ) in search_results
        ]

        prompt = self.prompt_builder.build(
            query=query,
            contexts=contexts,
            history=history,
        )

        client, config = (
            self.client_factory
            .create_for_knowledge_base(
                db=db,
                tenant_id=tenant_id,
                knowledge_base_id=knowledge_base_id,
            )
        )

        started_at = time.perf_counter()

        try:
            response = (
                client.chat.completions.create(
                    model=config.model_name,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                )
            )

        except AuthenticationError as exc:
            logger.exception(
                "Channel LLM authentication failed "
                "channel=%s kb=%s",
                chat_channel_id,
                knowledge_base_id,
            )

            raise (
                LLMAuthenticationError()
            ) from exc

        except RateLimitError as exc:
            logger.warning(
                "Channel LLM rate limited "
                "channel=%s kb=%s",
                chat_channel_id,
                knowledge_base_id,
            )

            raise (
                LLMRateLimitError()
            ) from exc

        except APITimeoutError as exc:
            logger.exception(
                "Channel LLM timeout "
                "channel=%s kb=%s",
                chat_channel_id,
                knowledge_base_id,
            )

            raise (
                LLMTimeoutError()
            ) from exc

        except APIConnectionError as exc:
            logger.exception(
                "Channel LLM connection failed "
                "channel=%s kb=%s",
                chat_channel_id,
                knowledge_base_id,
            )

            raise (
                LLMConnectionError()
            ) from exc

        except APIError as exc:
            logger.exception(
                "Channel LLM provider error "
                "channel=%s kb=%s",
                chat_channel_id,
                knowledge_base_id,
            )

            raise (
                LLMProviderError()
            ) from exc

        elapsed_ms = (
            (
                time.perf_counter()
                - started_at
            )
            * 1000
        )

        logger.info(
            "Channel LLM request completed "
            "channel=%s "
            "kb=%s "
            "model='%s' "
            "duration_ms=%.2f",
            chat_channel_id,
            knowledge_base_id,
            config.model_name,
            elapsed_ms,
        )

        answer = (
            response
            .choices[0]
            .message
            .content
            or ""
        )

        sources = self._build_sources(
            search_results
        )

        if self._is_no_answer(
            answer
        ):
            sources = []

        usage = {}

        if response.usage:
            usage = {
                "prompt_tokens":
                    response
                    .usage
                    .prompt_tokens,

                "completion_tokens":
                    response
                    .usage
                    .completion_tokens,

                "total_tokens":
                    response
                    .usage
                    .total_tokens,
            }

        self.conversation_service.save_assistant_message(
            db=db,
            conversation_id=conversation.id,
            content=answer,
            citations=sources,
            token_usage=usage,
        )

        return {
            "session_id":
                conversation.id,

            "answer":
                answer,

            "sources":
                sources,
        }

    def chat_stream(
        self,
        db: Session,
        tenant_id: UUID,
        chat_channel_id: UUID,
        knowledge_base_id: UUID,
        session_id: UUID | None,
        query: str,
    ) -> Generator[
        str,
        None,
        None,
    ]:
        conversation = (
            self.conversation_service
            .get_or_create_channel_conversation(
                db=db,
                tenant_id=tenant_id,
                chat_channel_id=chat_channel_id,
                knowledge_base_id=knowledge_base_id,
                conversation_id=session_id,
                title=query,
            )
        )

        self.conversation_service.save_user_message(
            db=db,
            conversation_id=conversation.id,
            content=query,
        )

        history = (
            self.conversation_service
            .get_messages(
                db=db,
                conversation_id=conversation.id,
            )
        )

        search_results = (
            self.search_service.search(
                db=db,
                knowledge_base_id=knowledge_base_id,
                query=query,
            )
        )

        contexts = [
            chunk.text
            for (
                chunk,
                document,
                knowledge_source,
                similarity,
            ) in search_results
        ]

        prompt = self.prompt_builder.build(
            query=query,
            contexts=contexts,
            history=history,
        )

        client, config = (
            self.client_factory
            .create_for_knowledge_base(
                db=db,
                tenant_id=tenant_id,
                knowledge_base_id=knowledge_base_id,
            )
        )

        started_at = time.perf_counter()

        answer = ""

        try:
            response = (
                client.chat.completions.create(
                    model=config.model_name,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    stream=True,
                )
            )

            for response_chunk in response:
                if (
                    not response_chunk.choices
                    or response_chunk
                    .choices[0]
                    .delta
                    .content
                    is None
                ):
                    continue

                token = (
                    response_chunk
                    .choices[0]
                    .delta
                    .content
                )

                answer += token

                yield (
                    f"data: {token}\n\n"
                )

        except AuthenticationError:
            logger.exception(
                "Streaming channel LLM "
                "authentication failed "
                "channel=%s kb=%s",
                chat_channel_id,
                knowledge_base_id,
            )

            yield self._stream_error_event(
                code=(
                    "LLM_AUTHENTICATION_FAILED"
                ),
                message=(
                    "The configured LLM "
                    "credentials are invalid."
                ),
            )

            yield self._stream_done_event()
            return

        except RateLimitError:
            logger.warning(
                "Streaming channel LLM "
                "rate limited "
                "channel=%s kb=%s",
                chat_channel_id,
                knowledge_base_id,
            )

            yield self._stream_error_event(
                code="LLM_RATE_LIMITED",
                message=(
                    "The LLM provider rate "
                    "limit has been reached. "
                    "Please try again later."
                ),
            )

            yield self._stream_done_event()
            return

        except APITimeoutError:
            logger.exception(
                "Streaming channel LLM "
                "timeout "
                "channel=%s kb=%s",
                chat_channel_id,
                knowledge_base_id,
            )

            yield self._stream_error_event(
                code="LLM_TIMEOUT",
                message=(
                    "The LLM provider did "
                    "not respond within the "
                    "expected time."
                ),
            )

            yield self._stream_done_event()
            return

        except APIConnectionError:
            logger.exception(
                "Streaming channel LLM "
                "connection failed "
                "channel=%s kb=%s",
                chat_channel_id,
                knowledge_base_id,
            )

            yield self._stream_error_event(
                code=(
                    "LLM_CONNECTION_FAILED"
                ),
                message=(
                    "The configured LLM "
                    "provider could not "
                    "be reached."
                ),
            )

            yield self._stream_done_event()
            return

        except APIError as exc:
            logger.exception(
                "Streaming channel LLM "
                "provider error "
                "channel=%s kb=%s "
                "error_type=%s",
                chat_channel_id,
                knowledge_base_id,
                type(exc).__name__,
            )

            yield self._stream_error_event(
                code="LLM_PROVIDER_ERROR",
                message=(
                    "The LLM provider "
                    "returned an error."
                ),
            )

            yield self._stream_done_event()
            return

        elapsed_ms = (
            (
                time.perf_counter()
                - started_at
            )
            * 1000
        )

        logger.info(
            "Streaming channel LLM "
            "request completed "
            "channel=%s "
            "kb=%s "
            "model='%s' "
            "duration_ms=%.2f",
            chat_channel_id,
            knowledge_base_id,
            config.model_name,
            elapsed_ms,
        )

        sources = self._build_sources(
            search_results
        )

        if self._is_no_answer(
            answer
        ):
            sources = []

        self.conversation_service.save_assistant_message(
            db=db,
            conversation_id=conversation.id,
            content=answer,
            citations=sources,
            token_usage={},
        )

        metadata = {
            "session_id":
                str(
                    conversation.id
                ),

            "sources":
                sources,
        }

        yield (
            "event: metadata\n"
            f"data: {json.dumps(metadata)}"
            "\n\n"
        )

        yield self._stream_done_event()