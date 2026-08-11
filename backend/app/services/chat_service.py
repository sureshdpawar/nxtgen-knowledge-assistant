from uuid import UUID

from sqlalchemy.orm import Session

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

    def chat(
        self,
        db: Session,
        tenant_id: UUID,
        knowledge_base_id: UUID,
        query: str,
    ) -> dict:

        search_results = self.search_service.search(
            db=db,
            knowledge_base_id=knowledge_base_id,
            query=query,
        )

        contexts = [
            chunk.text
            for chunk, document, knowledge_source, similarity
            in search_results
        ]

        prompt = self.prompt_builder.build(
            query=query,
            contexts=contexts,
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

        return {
            "answer": response.choices[0].message.content,
            "sources": sources,
        }