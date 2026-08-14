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
from app.services.conversation_service import (
    ConversationService,
)
from app.services.document_search_service import (
    DocumentSearchService,
)
from app.services.llm_client_factory import (
    LLMClientFactory,
)
from app.services.prompt_builder_service import (
    PromptBuilderService,
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
            "not enough information in the knowledge base",
            "the knowledge base does not contain enough information",
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
                            knowledge_source.id,
                        ),

                    "knowledge_source_name":
                        knowledge_source.name,

                    "document_id":
                        str(
                            document.id,
                        ),

                    "document_name":
                        document.original_filename,

                    "chunk_index":
                        chunk.chunk_index,

                    "page":
                        chunk.chunk_metadata.get(
                            "page",
                            1,
                        ),

                    "similarity":
                        round(
                            1 - float(
                                similarity,
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
        conversation_id: UUID | None,
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
                title=query,
            )
        )

        self.conversation_service.save_user_message(
            db=db,
            conversation_id=
                conversation.id,
            content=query,
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

        prompt = (
            self.prompt_builder.build(
                query=query,
                contexts=contexts,
                history=history,
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
            elapsed_ms = (
                (
                    time.perf_counter()
                    - started_at
                )
                * 1000
            )

            logger.error(
                "LLM authentication "
                "failed profile='%s' "
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
                type(exc).__name__,
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
                search_results,
            )
        )

        if self._is_no_answer(
            answer,
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
            conversation_id=
                conversation.id,
            content=answer,
            citations=sources,
            token_usage=usage,
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
        conversation_id: UUID | None,
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
                title=query,
            )
        )

        self.conversation_service.save_user_message(
            db=db,
            conversation_id=
                conversation.id,
            content=query,
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

        prompt = (
            self.prompt_builder.build(
                query=query,
                contexts=contexts,
                history=history,
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
                    code=
                        "LLM_AUTHENTICATION_FAILED",

                    message=
                        "The configured LLM "
                        "credentials are invalid.",
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

                    message=
                        "The LLM provider "
                        "rate limit has been "
                        "reached. Please try "
                        "again later.",
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

                    message=
                        "The LLM provider did "
                        "not respond within "
                        "the expected time.",
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
                    code=
                        "LLM_CONNECTION_FAILED",

                    message=
                        "The configured LLM "
                        "provider could not "
                        "be reached.",
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
                type(exc).__name__,
            )

            yield (
                self._stream_error_event(
                    code=
                        "LLM_PROVIDER_ERROR",

                    message=
                        "The LLM provider "
                        "returned an error.",
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
                search_results,
            )
        )

        if self._is_no_answer(
            answer,
        ):
            sources = []

        self.conversation_service.save_assistant_message(
            db=db,
            conversation_id=
                conversation.id,
            content=answer,
            citations=sources,
            token_usage={},
        )

        metadata = {
            "conversation_id":
                str(
                    conversation.id,
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