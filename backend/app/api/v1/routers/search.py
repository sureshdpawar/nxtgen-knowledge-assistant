from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.dependencies.rate_limit import (
    enforce_search_rate_limit,
)
from app.models.user import User
from app.schemas.search import (
    SearchRequest,
    SearchResponse,
    SearchResult,
)
from app.services.document_search_service import (
    DocumentSearchService,
)


router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


service = (
    DocumentSearchService()
)


@router.post(
    "",
    response_model=
        SearchResponse,
)
def search(
    payload:
        SearchRequest,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        enforce_search_rate_limit,
    ),
):
    rows = (
        service.search(
            db=db,
            knowledge_base_id=
                payload.knowledge_base_id,
            query=
                payload.query,
        )
    )

    results = []

    for (
        chunk,
        document,
        knowledge_source,
        score,
    ) in rows:

        results.append(
            SearchResult(
                knowledge_source_id=
                    knowledge_source.id,

                knowledge_source_name=
                    knowledge_source.name,

                document_id=
                    document.id,

                document_name=
                    document.original_filename,

                chunk_id=
                    chunk.id,

                chunk_index=
                    chunk.chunk_index,

                page=
                    chunk.chunk_metadata.get(
                        "page",
                        1,
                    ),

                similarity=
                    round(
                        1
                        - float(
                            score,
                        ),
                        3,
                    ),

                text=
                    chunk.text,
            )
        )

    return SearchResponse(
        results=results,
    )