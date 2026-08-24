from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.responses import (
    StreamingResponse,
)
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.dependencies.rate_limit import (
    enforce_chat_rate_limit,
)
from app.core.enums import (
    KnowledgeBaseAccessLevel,
)
from app.exceptions.usage import (
    UsageQuotaExceededError,
)
from app.models.user import User
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)
from app.services.chat_service import (
    ChatService,
)
from app.services.knowledge_base_access_service import (
    KnowledgeBaseAccessService,
)


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


service = (
    ChatService()
)

access_service = (
    KnowledgeBaseAccessService()
)


def _require_chat_access(
    *,
    db: Session,
    current_user: User,
    knowledge_base_id,
) -> None:
    """
    Require READ access before a user may
    chat against a Knowledge Base.

    MANAGE access also satisfies READ.

    Keeping this check in one helper ensures
    normal and streaming chat use exactly
    the same authorization policy.
    """

    access_service.require_access(
        db=db,
        current_user=current_user,
        knowledge_base_id=
            knowledge_base_id,
        required_level=
            KnowledgeBaseAccessLevel.READ,
    )


@router.post(
    "",
    response_model=
        ChatResponse,
)
def chat(
    payload: ChatRequest,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        enforce_chat_rate_limit,
    ),
):
    """
    Non-streaming Knowledge Base chat.

    Authorization is performed before:

    - conversation creation
    - retrieval
    - prompt construction
    - quota reservation
    - LLM invocation
    """

    _require_chat_access(
        db=db,
        current_user=current_user,
        knowledge_base_id=
            payload.knowledge_base_id,
    )

    try:
        result = (
            service.chat(
                db=db,
                tenant_id=
                    current_user.tenant_id,
                user_id=
                    current_user.id,
                knowledge_base_id=
                    payload
                    .knowledge_base_id,
                conversation_id=
                    payload
                    .conversation_id,
                query=
                    payload.query,
            )
        )

    except UsageQuotaExceededError as exc:
        raise HTTPException(
            status_code=
                status.HTTP_429_TOO_MANY_REQUESTS,
            detail=
                exc.to_dict(),
        ) from exc

    return ChatResponse(
        conversation_id=
            result[
                "conversation_id"
            ],

        answer=
            result[
                "answer"
            ],

        sources=
            result[
                "sources"
            ],
    )


@router.post(
    "/stream",
)
def chat_stream(
    payload: ChatRequest,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        enforce_chat_rate_limit,
    ),
):
    """
    Streaming Knowledge Base chat.

    Uses the exact same READ authorization
    policy as non-streaming chat.

    Authorization happens before creating
    the generator so unauthorized requests
    never begin retrieval or LLM execution.
    """

    _require_chat_access(
        db=db,
        current_user=current_user,
        knowledge_base_id=
            payload.knowledge_base_id,
    )

    generator = (
        service.chat_stream(
            db=db,
            tenant_id=
                current_user.tenant_id,
            user_id=
                current_user.id,
            knowledge_base_id=
                payload
                .knowledge_base_id,
            conversation_id=
                payload
                .conversation_id,
            query=
                payload.query,
        )
    )

    return StreamingResponse(
        generator,
        media_type=
            "text/event-stream",
        headers={
            "Cache-Control":
                "no-cache",

            "Connection":
                "keep-alive",

            "X-Accel-Buffering":
                "no",
        },
    )