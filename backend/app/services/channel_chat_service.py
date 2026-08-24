import json
import logging
import math
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
from app.exceptions.usage import (
    UsageQuotaExceededError,
)
from app.services.chat_service import (
    ChatService,
)
from app.services.llm_usage_service import (
    LLMUsageService,
)
from app.services.usage_quota_service import (
    UsageQuotaService,
)


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

    Channel chat additionally enforces:
    - tenant usage quotas
    - Knowledge Base usage quotas
    - ChatChannel usage quotas
    """

    def __init__(
        self,
    ):
        super().__init__()

        self.usage_quota_service = (
            UsageQuotaService()
        )

        self.llm_usage_service = (
            LLMUsageService()
        )

    def _estimate_tokens(
        self,
        text: str,
    ) -> int:
        """
        Lightweight provider-neutral token estimate.

        Actual provider usage is recorded whenever
        the provider returns token counts.

        This estimate is only used for the
        pre-request quota reservation and as a
        fallback for streaming usage.
        """

        if not text:
            return 0

        return max(
            1,
            math.ceil(
                len(text)
                / 4
            ),
        )

    def _check_quota(
        self,
        db: Session,
        *,
        tenant_id: UUID,
        knowledge_base_id: UUID,
        chat_channel_id: UUID,
        prompt: str,
        max_output_tokens: int,
    ) -> dict:
        estimated_input_tokens = (
            self._estimate_tokens(
                prompt
            )
        )

        return (
            self.usage_quota_service
            .check_chat_allowed(
                db=db,
                tenant_id=
                    tenant_id,
                knowledge_base_id=
                    knowledge_base_id,
                chat_channel_id=
                    chat_channel_id,
                estimated_input_tokens=
                    estimated_input_tokens,
                reserved_output_tokens=
                    max_output_tokens,
            )
        )

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
                tenant_id=
                    tenant_id,
                chat_channel_id=
                    chat_channel_id,
                knowledge_base_id=
                    knowledge_base_id,
                conversation_id=
                    session_id,
                title=
                    query,
            )
        )

        #
        # Load only previous conversation
        # messages before adding the current
        # user turn.
        #
        history = (
            self.conversation_service
            .get_messages(
                db=db,
                conversation_id=
                    conversation.id,
            )
        )

        search_results = (
            self.search_service.search(
                db=db,
                knowledge_base_id=
                    knowledge_base_id,
                query=
                    query,
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

        prompt = (
            self.prompt_builder.build(
                query=
                    query,
                contexts=
                    contexts,
                history=
                    history,
            )
        )

        client, config = (
            self.client_factory
            .create_for_knowledge_base(
                db=db,
                tenant_id=
                    tenant_id,
                knowledge_base_id=
                    knowledge_base_id,
            )
        )

        #
        # HARD QUOTA CHECK
        #
        # This runs before:
        #
        # - saving the current user message
        # - making the provider request
        #
        # Therefore blocked requests consume
        # no LLM budget.
        #
        self._check_quota(
            db=db,
            tenant_id=
                tenant_id,
            knowledge_base_id=
                knowledge_base_id,
            chat_channel_id=
                chat_channel_id,
            prompt=
                prompt,
            max_output_tokens=
                config.max_tokens,
        )

        #
        # The request has passed quota checks,
        # so persist the user turn.
        #
        self.conversation_service.save_user_message(
            db=db,
            conversation_id=
                conversation.id,
            content=
                query,
        )

        started_at = (
            time.perf_counter()
        )

        try:
            response = (
                client.chat.completions.create(
                    model=
                        config.model_name,
                    messages=[
                        {
                            "role":
                                "user",
                            "content":
                                prompt,
                        }
                    ],
                    temperature=
                        config.temperature,
                    max_tokens=
                        config.max_tokens,
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

        sources = (
            self._build_sources(
                search_results
            )
        )

        if self._is_no_answer(
            answer
        ):
            sources = []

        usage = {}

        input_tokens = 0
        output_tokens = 0

        if response.usage:
            input_tokens = int(
                response
                .usage
                .prompt_tokens
                or 0
            )

            output_tokens = int(
                response
                .usage
                .completion_tokens
                or 0
            )

            usage = {
                "prompt_tokens":
                    input_tokens,

                "completion_tokens":
                    output_tokens,

                "total_tokens":
                    int(
                        response
                        .usage
                        .total_tokens
                        or (
                            input_tokens
                            + output_tokens
                        )
                    ),
            }

        else:
            #
            # Provider did not return usage.
            # Fall back to estimation so the
            # request is still metered.
            #
            input_tokens = (
                self._estimate_tokens(
                    prompt
                )
            )

            output_tokens = (
                self._estimate_tokens(
                    answer
                )
            )

            usage = {
                "prompt_tokens":
                    input_tokens,

                "completion_tokens":
                    output_tokens,

                "total_tokens":
                    (
                        input_tokens
                        + output_tokens
                    ),

                "estimated":
                    True,
            }

        assistant_message = (
            self.conversation_service
            .save_assistant_message(
                db=db,
                conversation_id=
                    conversation.id,
                content=
                    answer,
                citations=
                    sources,
                token_usage=
                    usage,
            )
        )

        #
        # Record normalized usage for
        # quota enforcement/reporting.
        #
        self.llm_usage_service.record(
            db=db,
            tenant_id=
                tenant_id,
            knowledge_base_id=
                knowledge_base_id,
            chat_channel_id=
                chat_channel_id,
            conversation_id=
                conversation.id,
            message_id=
                assistant_message.id,
            provider=
                config.provider.value,
            model=
                config.model_name,
            input_tokens=
                input_tokens,
            output_tokens=
                output_tokens,
            request_type=
                "chat",
            usage_metadata={
                "provider_usage":
                    usage,
                "estimated":
                    bool(
                        usage.get(
                            "estimated",
                            False,
                        )
                    ),
            },
        )

        db.commit()

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
                tenant_id=
                    tenant_id,
                chat_channel_id=
                    chat_channel_id,
                knowledge_base_id=
                    knowledge_base_id,
                conversation_id=
                    session_id,
                title=
                    query,
            )
        )

        history = (
            self.conversation_service
            .get_messages(
                db=db,
                conversation_id=
                    conversation.id,
            )
        )

        search_results = (
            self.search_service.search(
                db=db,
                knowledge_base_id=
                    knowledge_base_id,
                query=
                    query,
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

        prompt = (
            self.prompt_builder.build(
                query=
                    query,
                contexts=
                    contexts,
                history=
                    history,
            )
        )

        client, config = (
            self.client_factory
            .create_for_knowledge_base(
                db=db,
                tenant_id=
                    tenant_id,
                knowledge_base_id=
                    knowledge_base_id,
            )
        )

        #
        # Streaming quota check.
        #
        # If blocked, return a structured SSE
        # error without making the LLM request.
        #
        try:
            self._check_quota(
                db=db,
                tenant_id=
                    tenant_id,
                knowledge_base_id=
                    knowledge_base_id,
                chat_channel_id=
                    chat_channel_id,
                prompt=
                    prompt,
                max_output_tokens=
                    config.max_tokens,
            )

        except UsageQuotaExceededError as exc:
            logger.warning(
                "Channel usage quota exceeded "
                "tenant=%s channel=%s kb=%s "
                "scope=%s period=%s metric=%s",
                tenant_id,
                chat_channel_id,
                knowledge_base_id,
                exc.scope,
                exc.period,
                exc.metric,
            )

            yield (
                self._stream_error_event(
                    code=
                        "USAGE_LIMIT_REACHED",
                    message=
                        exc.message,
                )
            )

            yield (
                self._stream_done_event()
            )

            return

        self.conversation_service.save_user_message(
            db=db,
            conversation_id=
                conversation.id,
            content=
                query,
        )

        started_at = (
            time.perf_counter()
        )

        answer = ""

        try:
            response = (
                client.chat.completions.create(
                    model=
                        config.model_name,
                    messages=[
                        {
                            "role":
                                "user",
                            "content":
                                prompt,
                        }
                    ],
                    temperature=
                        config.temperature,
                    max_tokens=
                        config.max_tokens,
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
            elapsed_ms = (
                (
                    time.perf_counter()
                    - started_at
                )
                * 1000
            )

            logger.exception(
                "Streaming channel LLM "
                "authentication failed "
                "channel=%s kb=%s "
                "duration_ms=%.2f",
                chat_channel_id,
                knowledge_base_id,
                elapsed_ms,
            )

            yield (
                self._stream_error_event(
                    code=(
                        "LLM_AUTHENTICATION_FAILED"
                    ),
                    message=(
                        "The configured LLM "
                        "credentials are invalid."
                    ),
                )
            )

            yield (
                self._stream_done_event()
            )

            return

        except RateLimitError:
            elapsed_ms = (
                (
                    time.perf_counter()
                    - started_at
                )
                * 1000
            )

            logger.warning(
                "Streaming channel LLM "
                "rate limited "
                "channel=%s kb=%s "
                "duration_ms=%.2f",
                chat_channel_id,
                knowledge_base_id,
                elapsed_ms,
            )

            yield (
                self._stream_error_event(
                    code=
                        "LLM_RATE_LIMITED",
                    message=(
                        "The LLM provider rate "
                        "limit has been reached. "
                        "Please try again later."
                    ),
                )
            )

            yield (
                self._stream_done_event()
            )

            return

        except APITimeoutError:
            elapsed_ms = (
                (
                    time.perf_counter()
                    - started_at
                )
                * 1000
            )

            logger.exception(
                "Streaming channel LLM timeout "
                "channel=%s kb=%s "
                "duration_ms=%.2f",
                chat_channel_id,
                knowledge_base_id,
                elapsed_ms,
            )

            yield (
                self._stream_error_event(
                    code=
                        "LLM_TIMEOUT",
                    message=(
                        "The LLM provider did "
                        "not respond within "
                        "the expected time."
                    ),
                )
            )

            yield (
                self._stream_done_event()
            )

            return

        except APIConnectionError:
            elapsed_ms = (
                (
                    time.perf_counter()
                    - started_at
                )
                * 1000
            )

            logger.exception(
                "Streaming channel LLM "
                "connection failed "
                "channel=%s kb=%s "
                "duration_ms=%.2f",
                chat_channel_id,
                knowledge_base_id,
                elapsed_ms,
            )

            yield (
                self._stream_error_event(
                    code=(
                        "LLM_CONNECTION_FAILED"
                    ),
                    message=(
                        "The configured LLM "
                        "provider could not "
                        "be reached."
                    ),
                )
            )

            yield (
                self._stream_done_event()
            )

            return

        except APIError as exc:
            elapsed_ms = (
                (
                    time.perf_counter()
                    - started_at
                )
                * 1000
            )

            logger.exception(
                "Streaming channel LLM "
                "provider error "
                "channel=%s kb=%s "
                "duration_ms=%.2f "
                "error_type=%s",
                chat_channel_id,
                knowledge_base_id,
                elapsed_ms,
                type(
                    exc
                ).__name__,
            )

            yield (
                self._stream_error_event(
                    code=
                        "LLM_PROVIDER_ERROR",
                    message=(
                        "The LLM provider "
                        "returned an error."
                    ),
                )
            )

            yield (
                self._stream_done_event()
            )

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

        sources = (
            self._build_sources(
                search_results
            )
        )

        if self._is_no_answer(
            answer
        ):
            sources = []

        #
        # Current streaming provider call does
        # not expose response.usage.
        #
        # Until we explicitly enable provider
        # streaming usage support, meter the
        # completed stream using the same
        # provider-neutral estimator.
        #
        input_tokens = (
            self._estimate_tokens(
                prompt
            )
        )

        output_tokens = (
            self._estimate_tokens(
                answer
            )
        )

        usage = {
            "prompt_tokens":
                input_tokens,

            "completion_tokens":
                output_tokens,

            "total_tokens":
                (
                    input_tokens
                    + output_tokens
                ),

            "estimated":
                True,

            "streaming":
                True,
        }

        assistant_message = (
            self.conversation_service
            .save_assistant_message(
                db=db,
                conversation_id=
                    conversation.id,
                content=
                    answer,
                citations=
                    sources,
                token_usage=
                    usage,
            )
        )

        self.llm_usage_service.record(
            db=db,
            tenant_id=
                tenant_id,
            knowledge_base_id=
                knowledge_base_id,
            chat_channel_id=
                chat_channel_id,
            conversation_id=
                conversation.id,
            message_id=
                assistant_message.id,
            provider=
                config.provider.value,
            model=
                config.model_name,
            input_tokens=
                input_tokens,
            output_tokens=
                output_tokens,
            request_type=
                "chat",
            usage_metadata={
                "estimated":
                    True,
                "streaming":
                    True,
            },
        )

        db.commit()

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
            f"data: "
            f"{json.dumps(metadata)}"
            "\n\n"
        )

        yield (
            self._stream_done_event()
        )