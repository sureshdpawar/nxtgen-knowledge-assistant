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
        self.search_service = DocumentSearchService()
        self.prompt_builder = PromptBuilderService()
        self.client_factory = LLMClientFactory()
        self.conversation_service = (
            ConversationService()
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
            self.conversation_service.get_or_create_conversation(
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
            self.conversation_service.get_messages(
                db=db,
                conversation_id=conversation.id,
            )
        )

        search_results = self.search_service.search(
            db=db,
            knowledge_base_id=knowledge_base_id,
            query=query,
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

        client, config = self.client_factory.create(
            db=db,
            tenant_id=tenant_id,
        )

        response = client.chat.completions.create(
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

        answer = (
            response.choices[0]
            .message.content
        )

        sources = []

        for (
            chunk,
            document,
            knowledge_source,
            similarity,
        ) in search_results:

            sources.append(
                {
                    "knowledge_source_name": knowledge_source.name,
                    "document_name": document.original_filename,
                    "chunk_index": chunk.chunk_index,
                    "page": chunk.chunk_metadata.get(
                        "page",
                        1,
                    ),
                    "similarity": round(
                        1 - float(similarity),
                        3,
                    ),
                }
            )

        usage = {}

        if response.usage:

            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

        self.conversation_service.save_assistant_message(
            db=db,
            conversation_id=conversation.id,
            content=answer,
            citations=sources,
            token_usage=usage,
        )

        return {
            "conversation_id": conversation.id,
            "answer": answer,
            "sources": sources,
        }