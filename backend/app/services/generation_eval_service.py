import time

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.knowledge_base import (
    KnowledgeBase,
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


class GenerationEvalService:

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

    def _estimate_tokens(
        self,
        text: str,
    ) -> int:
        """
        Fallback token estimation.

        Used only when the LLM provider
        does not return token usage.
        """

        if not text:
            return 0

        return max(
            1,
            len(text) // 4,
        )

    def evaluate_case(
        self,
        db: Session,
        knowledge_base_id: UUID,
        question: str,
        top_k: int,
    ) -> dict:
        """
        Execute one complete RAG evaluation
        case.

        Captures:

        - retrieval results
        - document IDs
        - document external IDs
        - chunk IDs
        - distances
        - retrieved context
        - generated answer
        - prompt
        - latency
        - token usage
        - LLM profile metadata

        Retrieval quality scoring is handled
        separately by retrieval evaluators.
        """

        if top_k < 1:
            raise ValueError(
                "top_k must be greater than 0."
            )

        knowledge_base = db.get(
            KnowledgeBase,
            knowledge_base_id,
        )

        if knowledge_base is None:
            raise ValueError(
                "Knowledge Base not found."
            )

        #
        # Retrieval
        #
        retrieval_started_at = (
            time.perf_counter()
        )

        search_results = (
            self.search_service.search(
                db=db,

                knowledge_base_id=
                    knowledge_base_id,

                query=
                    question,

                top_k_override=
                    top_k,
            )
        )

        retrieval_latency_ms = (
            (
                time.perf_counter()
                - retrieval_started_at
            )
            * 1000
        )

        retrieved_document_ids = []

        retrieved_document_external_ids = []

        retrieved_chunk_ids = []

        retrieved_distances = []

        retrieval_context = []

        contexts = []

        for (
            rank,
            result,
        ) in enumerate(
            search_results,
            start=1,
        ):
            (
                chunk,
                document,
                knowledge_source,
                distance,
            ) = result

            document_id = str(
                document.id
            )

            document_external_id = (
                document.external_id
            )

            chunk_id = str(
                chunk.id
            )

            chunk_text = (
                chunk.text
                or ""
            )

            retrieved_document_ids.append(
                document_id
            )

            #
            # Keep this list aligned with
            # retrieved_document_ids.
            #
            # external_id may be None for
            # some ingestion types.
            #
            retrieved_document_external_ids.append(
                document_external_id
            )

            retrieved_chunk_ids.append(
                chunk_id
            )

            retrieved_distances.append(
                float(
                    distance
                )
            )

            contexts.append(
                chunk_text
            )

            retrieval_context.append(
                {
                    "rank":
                        rank,

                    "document_id":
                        document_id,

                    #
                    # Stable source identity.
                    #
                    # For website ingestion
                    # this is currently the
                    # source page URL.
                    #
                    "document_external_id":
                        document_external_id,

                    "chunk_id":
                        chunk_id,

                    "document_name":
                        document.original_filename,

                    "knowledge_source_id":
                        str(
                            knowledge_source.id
                        ),

                    "knowledge_source_name":
                        knowledge_source.name,

                    "chunk_index":
                        chunk.chunk_index,

                    "text":
                        chunk_text,

                    "distance":
                        float(
                            distance
                        ),
                }
            )

        #
        # Build grounded prompt.
        #
        prompt = (
            self.prompt_builder.build(
                query=
                    question,

                contexts=
                    contexts,

                history=[],
            )
        )

        #
        # Resolve Knowledge Base
        # LLM profile.
        #
        client, config = (
            self.client_factory
            .create_for_knowledge_base(
                db=db,

                tenant_id=
                    knowledge_base.tenant_id,

                knowledge_base_id=
                    knowledge_base_id,
            )
        )

        #
        # Generate answer.
        #
        generation_started_at = (
            time.perf_counter()
        )

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

        generation_latency_ms = (
            (
                time.perf_counter()
                - generation_started_at
            )
            * 1000
        )

        #
        # Extract generated answer.
        #
        actual_answer = ""

        if (
            response.choices
            and response.choices[0].message
        ):
            actual_answer = (
                response
                .choices[0]
                .message
                .content
                or ""
            )

        actual_answer = (
            actual_answer.strip()
        )

        #
        # Token usage.
        #
        # Prefer provider-reported usage.
        #
        # Fall back to a rough estimate
        # when usage is unavailable.
        #
        if response.usage:
            prompt_tokens = int(
                response
                .usage
                .prompt_tokens
                or 0
            )

            completion_tokens = int(
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
                    prompt_tokens
                    + completion_tokens
                )
            )

            usage_estimated = False

        else:
            prompt_tokens = (
                self._estimate_tokens(
                    prompt
                )
            )

            completion_tokens = (
                self._estimate_tokens(
                    actual_answer
                )
            )

            total_tokens = (
                prompt_tokens
                + completion_tokens
            )

            usage_estimated = True

        total_latency_ms = (
            retrieval_latency_ms
            + generation_latency_ms
        )

        #
        # Capture the exact LLM profile
        # used for this evaluation case.
        #
        llm_metadata = {
            "profile_id":
                (
                    str(
                        config.id
                    )
                    if getattr(
                        config,
                        "id",
                        None,
                    )
                    else None
                ),

            "profile_name":
                getattr(
                    config,
                    "name",
                    None,
                ),

            "provider":
                (
                    config.provider.value
                    if getattr(
                        config,
                        "provider",
                        None,
                    )
                    else None
                ),

            "model":
                config.model_name,

            "temperature":
                config.temperature,

            "max_tokens":
                config.max_tokens,
        }

        usage = {
            "prompt_tokens":
                prompt_tokens,

            "completion_tokens":
                completion_tokens,

            "total_tokens":
                total_tokens,

            "estimated":
                usage_estimated,
        }

        latency = {
            "retrieval_ms":
                round(
                    retrieval_latency_ms,
                    2,
                ),

            "generation_ms":
                round(
                    generation_latency_ms,
                    2,
                ),

            "total_ms":
                round(
                    total_latency_ms,
                    2,
                ),
        }

        return {
            "question":
                question,

            "actual_answer":
                actual_answer,

            #
            # Environment-specific
            # identifiers.
            #
            "retrieved_document_ids":
                retrieved_document_ids,

            #
            # Portable source identifiers.
            #
            # For website documents these
            # are URLs.
            #
            "retrieved_document_external_ids":
                retrieved_document_external_ids,

            "retrieved_chunk_ids":
                retrieved_chunk_ids,

            "retrieved_distances":
                retrieved_distances,

            #
            # Rich retrieval trace.
            #
            # Each context now contains:
            #
            # document_id
            # document_external_id
            # chunk_id
            # rank
            # text
            # distance
            #
            "retrieval_context":
                retrieval_context,

            "prompt":
                prompt,

            "usage":
                usage,

            "latency":
                latency,

            "llm":
                llm_metadata,
        }