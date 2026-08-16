import json

from uuid import UUID

from langchain.tools import tool
from sqlalchemy.orm import Session

from app.services.document_search_service import (
    DocumentSearchService,
)


def create_knowledge_search_tool(
    db: Session,
    knowledge_base_ids: list[UUID],
):

    search_service = (
        DocumentSearchService()
    )

    @tool
    def search_knowledge(
        query: str,
    ) -> str:
        """
        Search the enterprise knowledge bases
        assigned to this agent.

        Use this tool when company-specific
        documentation, policies, procedures,
        runbooks, manuals, or internal
        knowledge may help answer the user's
        question.
        """

        query = query.strip()

        if not query:
            return json.dumps(
                {
                    "results": [],
                    "message":
                        "Search query is empty.",
                }
            )

        if not knowledge_base_ids:
            return json.dumps(
                {
                    "results": [],
                    "message":
                        (
                            "No knowledge bases "
                            "are assigned to "
                            "this agent."
                        ),
                }
            )

        results = []

        for knowledge_base_id in (
            knowledge_base_ids
        ):
            rows = (
                search_service.search(
                    db=db,
                    knowledge_base_id=
                        knowledge_base_id,
                    query=query,
                )
            )

            for (
                chunk,
                document,
                knowledge_source,
                score,
            ) in rows:

                results.append(
                    {
                        "knowledge_base_id":
                            str(
                                knowledge_base_id
                            ),

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
                            (
                                document
                                .original_filename
                            ),

                        "chunk_id":
                            str(
                                chunk.id
                            ),

                        "chunk_index":
                            chunk.chunk_index,

                        "page":
                            (
                                chunk
                                .chunk_metadata
                                .get(
                                    "page",
                                    1,
                                )
                            ),

                        "similarity":
                            round(
                                1
                                - float(
                                    score
                                ),
                                3,
                            ),

                        "text":
                            chunk.text,
                    }
                )

        results.sort(
            key=lambda item:
                item[
                    "similarity"
                ],
            reverse=True,
        )

        #
        # Keep tool output bounded.
        #
        results = results[:5]

        return json.dumps(
            {
                "query":
                    query,

                "results":
                    results,
            },
            ensure_ascii=False,
        )

    return search_knowledge