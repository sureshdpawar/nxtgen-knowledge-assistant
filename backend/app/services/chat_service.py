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
from app.services.conversation_service import (
    ConversationService,
)
from app.services.document_search_service import (
    DocumentSearchService,
)
from app.services.llm_client_factory import (
    LLMClientFactory,
)
from app.services.llm_usage_service import (
    LLMUsageService,
)
from app.services.prompt_builder_service import (
    PromptBuilderService,
)
from app.services.usage_quota_service import (
    UsageQuotaService,
)


logger = logging.getLogger(
    "nxtgen.llm"
)


class ChatService:

    def __init__(self):
        self.search_service = (
            DocumentSearchService()
        )

        self.prompt_builder = (
            PromptBuilderService()
        )

        self.client_factory = (
            LLMClientFactory()
        )

        self.conversation_service = (
            ConversationService()
        )

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
        Lightweight provider-neutral estimate.

        Used only for:
        - quota reservation before the request
        - streaming fallback usage

        Exact provider usage is preferred
        whenever available.
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
        prompt: str,
        max_output_tokens: int,
        chat_channel_id: (
            UUID | None
        ) = None,
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

    def _build_usage(
        self,
        *,
        response,
        prompt: str,
        answer: str,
    ) -> tuple[
        dict,
        int,
        int,
    ]:
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

            total_tokens = int(
                response
                .usage
                .total_tokens
                or (
                    input_tokens
                    + output_tokens
                )
            )

            usage = {
                "prompt_tokens":
                    input_tokens,

                "completion_tokens":
                    output_tokens,

                "total_tokens":
                    total_tokens,

                "estimated":
                    False,
            }

            return (
                usage,
                input_tokens,
                output_tokens,
            )

        #
        # Fallback for an OpenAI-compatible
        # provider that does not return usage.
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

        return (
            usage,
            input_tokens,
            output_tokens,
        )

    def _is_no_answer(
        self,
        answer: str,
    ) -> bool:
        normalized = (
            answer
            .strip()
            .lower()
        )

        no_answer_phrases = [
            "i don't have enough information",
            "i do not have enough information",
            (
                "not enough information "
                "in the knowledge base"
            ),
            (
                "the knowledge base does not "
                "contain enough information"
            ),
        ]

        return any(
            phrase in normalized
            for phrase
            in no_answer_phrases
        )

    def _build_sources(
        self,
        search_results,
    ) -> list[dict]:
        sources = []

        for (
            chunk,
            document,
            knowledge_source,
            similarity,
        ) in search_results:
            sources.append(
                {
                    "knowledge_source_id":
                        str(
                            knowledge_source.id
                        ),

                    "knowledge_source_name":
                        knowledge_source.name,

                    "document_id":
                        str(
                            document.id
                        ),

                    "document_name":
                        document
                        .original_filename,

                    "chunk_index":
                        chunk.chunk_index,

                    "page":
                        chunk
                        .chunk_metadata
                        .get(
                            "page",
                            1,
                        ),

                    "similarity":
                        round(
                            1
                            - float(
                                similarity
                            ),
                            3,
                        ),
                }
            )

        return sources

    def _stream_error_event(
        self,
        code: str,
        message: str,
    ) -> str:
        payload = {
            "code":
                code,

            "message":
                message,
        }

        return (
            "event: error\n"
            f"data: {json.dumps(payload)}"
            "\n\n"
        )

    def _stream_done_event(
        self,
    ) -> str:
        return (
            "event: done\n"
            "data: [DONE]\n\n"
        )

    def chat(
        self,
        db: Session,
        tenant_id: UUID,
        user_id: UUID,
        knowledge_base_id: UUID,
        conversation_id: (
            UUID | None
        ),
        query: str,
    ) -> dict:
        conversation = (
            self.conversation_service
            .get_or_create_conversation(
                db=db,
                tenant_id=
                    tenant_id,
                user_id=
                    user_id,
                knowledge_base_id=
                    knowledge_base_id,
                conversation_id=
                    conversation_id,
                title=
                    query,
            )
        )

        #
        # IMPORTANT:
        #
        # Load history BEFORE saving the
        # current question.
        #
        # PromptBuilder already has a
        # Current Question section.
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
        # Quota is checked BEFORE:
        #
        # - current user message is saved
        # - provider request is made
        #
        self._check_quota(
            db=db,
            tenant_id=
                tenant_id,
            knowledge_base_id=
                knowledge_base_id,
            prompt=
                prompt,
            max_output_tokens=
                config.max_tokens,
        )

        #
        # Quota passed.
        #
        (
            self.conversation_service
            .save_user_message(
                db=db,
                conversation_id=
                    conversation.id,
                content=
                    query,
            )
        )

        started_at = (
            time.perf_counter()
        )

        try:
            response = (
                client.chat.completions
                .create(
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
            elapsed_ms = (
                (
                    time.perf_counter()
                    - started_at
                )
                * 1000
            )

            logger.error(
                "LLM authentication failed "
                "profile='%s' "
                "model='%s' "
                "provider='%s' "
                "kb=%s "
                "duration_ms=%.2f",
                config.name,
                config.model_name,
                config.provider.value,
                knowledge_base_id,
                elapsed_ms,
            )

            raise (
                LLMAuthenticationError()
            ) from exc

        except RateLimitError as exc:
            elapsed_ms = (
                (
                    time.perf_counter()
                    - started_at
                )
                * 1000
            )

            logger.warning(
                "LLM rate limited "
                "profile='%s' "
                "model='%s' "
                "provider='%s' "
                "kb=%s "
                "duration_ms=%.2f",
                config.name,
                config.model_name,
                config.provider.value,
                knowledge_base_id,
                elapsed_ms,
            )

            raise (
                LLMRateLimitError()
            ) from exc

        except APITimeoutError as exc:
            elapsed_ms = (
                (
                    time.perf_counter()
                    - started_at
                )
                * 1000
            )

            logger.error(
                "LLM timeout "
                "profile='%s' "
                "model='%s' "
                "provider='%s' "
                "kb=%s "
                "duration_ms=%.2f",
                config.name,
                config.model_name,
                config.provider.value,
                knowledge_base_id,
                elapsed_ms,
            )

            raise (
                LLMTimeoutError()
            ) from exc

        except APIConnectionError as exc:
            elapsed_ms = (
                (
                    time.perf_counter()
                    - started_at
                )
                * 1000
            )

            logger.error(
                "LLM connection failed "
                "profile='%s' "
                "model='%s' "
                "provider='%s' "
                "kb=%s "
                "duration_ms=%.2f",
                config.name,
                config.model_name,
                config.provider.value,
                knowledge_base_id,
                elapsed_ms,
            )

            raise (
                LLMConnectionError()
            ) from exc

        except APIError as exc:
            elapsed_ms = (
                (
                    time.perf_counter()
                    - started_at
                )
                * 1000
            )

            logger.error(
                "LLM provider error "
                "profile='%s' "
                "model='%s' "
                "provider='%s' "
                "kb=%s "
                "duration_ms=%.2f "
                "error_type='%s'",
                config.name,
                config.model_name,
                config.provider.value,
                knowledge_base_id,
                elapsed_ms,
                type(
                    exc
                ).__name__,
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
            "LLM request completed "
            "profile='%s' "
            "model='%s' "
            "provider='%s' "
            "kb=%s "
            "duration_ms=%.2f",
            config.name,
            config.model_name,
            config.provider.value,
            knowledge_base_id,
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

        (
            usage,
            input_tokens,
            output_tokens,
        ) = self._build_usage(
            response=
                response,
            prompt=
                prompt,
            answer=
                answer,
        )

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
        # Normalized usage record.
        #
        self.llm_usage_service.record(
            db=db,
            tenant_id=
                tenant_id,
            knowledge_base_id=
                knowledge_base_id,
            chat_channel_id=
                None,
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

                "streaming":
                    False,
            },
        )

        db.commit()

        logger.info(
            "LLM usage recorded "
            "tenant=%s "
            "kb=%s "
            "conversation=%s "
            "input_tokens=%s "
            "output_tokens=%s "
            "total_tokens=%s",
            tenant_id,
            knowledge_base_id,
            conversation.id,
            input_tokens,
            output_tokens,
            (
                input_tokens
                + output_tokens
            ),
        )

        return {
            "conversation_id":
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
        user_id: UUID,
        knowledge_base_id: UUID,
        conversation_id: (
            UUID | None
        ),
        query: str,
    ) -> Generator[
        str,
        None,
        None,
    ]:
        conversation = (
            self.conversation_service
            .get_or_create_conversation(
                db=db,
                tenant_id=
                    tenant_id,
                user_id=
                    user_id,
                knowledge_base_id=
                    knowledge_base_id,
                conversation_id=
                    conversation_id,
                title=
                    query,
            )
        )

        #
        # Previous messages only.
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
        # Streaming quota check.
        #
        try:
            self._check_quota(
                db=db,
                tenant_id=
                    tenant_id,
                knowledge_base_id=
                    knowledge_base_id,
                prompt=
                    prompt,
                max_output_tokens=
                    config.max_tokens,
            )

        except UsageQuotaExceededError as exc:
            logger.warning(
                "Usage quota exceeded "
                "tenant=%s "
                "kb=%s "
                "scope=%s "
                "period=%s "
                "metric=%s",
                tenant_id,
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

        (
            self.conversation_service
            .save_user_message(
                db=db,
                conversation_id=
                    conversation.id,
                content=
                    query,
            )
        )

        started_at = (
            time.perf_counter()
        )

        answer = ""

        try:
            response = (
                client.chat.completions
                .create(
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

            logger.error(
                "Streaming LLM "
                "authentication failed "
                "profile='%s' "
                "model='%s' "
                "provider='%s' "
                "kb=%s "
                "duration_ms=%.2f",
                config.name,
                config.model_name,
                config.provider.value,
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
                "Streaming LLM "
                "rate limited "
                "profile='%s' "
                "model='%s' "
                "provider='%s' "
                "kb=%s "
                "duration_ms=%.2f",
                config.name,
                config.model_name,
                config.provider.value,
                knowledge_base_id,
                elapsed_ms,
            )

            yield (
                self._stream_error_event(
                    code=
                        "LLM_RATE_LIMITED",
                    message=(
                        "The LLM provider "
                        "rate limit has been "
                        "reached. Please try "
                        "again later."
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

            logger.error(
                "Streaming LLM timeout "
                "profile='%s' "
                "model='%s' "
                "provider='%s' "
                "kb=%s "
                "duration_ms=%.2f",
                config.name,
                config.model_name,
                config.provider.value,
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

            logger.error(
                "Streaming LLM "
                "connection failed "
                "profile='%s' "
                "model='%s' "
                "provider='%s' "
                "kb=%s "
                "duration_ms=%.2f",
                config.name,
                config.model_name,
                config.provider.value,
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

            logger.error(
                "Streaming LLM "
                "provider error "
                "profile='%s' "
                "model='%s' "
                "provider='%s' "
                "kb=%s "
                "duration_ms=%.2f "
                "error_type='%s'",
                config.name,
                config.model_name,
                config.provider.value,
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
            "Streaming LLM request "
            "completed "
            "profile='%s' "
            "model='%s' "
            "provider='%s' "
            "kb=%s "
            "duration_ms=%.2f",
            config.name,
            config.model_name,
            config.provider.value,
            knowledge_base_id,
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
        # Current streaming call does not
        # return provider usage metadata.
        #
        # Meter conservatively using the
        # same estimation method.
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
                None,
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

        logger.info(
            "Streaming LLM usage recorded "
            "tenant=%s "
            "kb=%s "
            "conversation=%s "
            "input_tokens=%s "
            "output_tokens=%s "
            "total_tokens=%s",
            tenant_id,
            knowledge_base_id,
            conversation.id,
            input_tokens,
            output_tokens,
            (
                input_tokens
                + output_tokens
            ),
        )

        metadata = {
            "conversation_id":
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