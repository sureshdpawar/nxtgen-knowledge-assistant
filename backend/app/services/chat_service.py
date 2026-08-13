import json

from collections.abc import Generator
from uuid import UUID

from sqlalchemy.orm import Session

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
                            knowledge_source.id
                        ),

                    "knowledge_source_name":
                        knowledge_source.name,

                    "document_id":
                        str(
                            document.id
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
                                similarity
                            ),
                            3,
                        ),
                }
            )

        return sources

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
                tenant_id=tenant_id,
                user_id=user_id,
                conversation_id=conversation_id,
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

        prompt = (
            self.prompt_builder.build(
                query=query,
                contexts=contexts,
                history=history,
            )
        )

        client, config = (
            self.client_factory.create(
                db=db,
                tenant_id=tenant_id,
            )
        )

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
                    response.usage.prompt_tokens,

                "completion_tokens":
                    response.usage.completion_tokens,

                "total_tokens":
                    response.usage.total_tokens,
            }

        self.conversation_service.save_assistant_message(
            db=db,
            conversation_id=conversation.id,
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
    ) -> Generator[str, None, None]:

        conversation = (
            self.conversation_service
            .get_or_create_conversation(
                db=db,
                tenant_id=tenant_id,
                user_id=user_id,
                conversation_id=conversation_id,
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

        prompt = (
            self.prompt_builder.build(
                query=query,
                contexts=contexts,
                history=history,
            )
        )

        client, config = (
            self.client_factory.create(
                db=db,
                tenant_id=tenant_id,
            )
        )

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

        answer = ""

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
            conversation_id=conversation.id,
            content=answer,
            citations=sources,
            token_usage={},
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
            f"data: {json.dumps(metadata)}\n\n"
        )

        yield (
            "event: done\n"
            "data: [DONE]\n\n"
        )