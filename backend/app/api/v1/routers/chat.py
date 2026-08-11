from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)
from app.services.chat_service import (
    ChatService,
)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

service = ChatService()


@router.post(
    "",
    response_model=ChatResponse,
)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_active_user,
    ),
):

    result = service.chat(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        knowledge_base_id=payload.knowledge_base_id,
        conversation_id=payload.conversation_id,
        query=payload.query,
    )

    return ChatResponse(
        conversation_id=result["conversation_id"],
        answer=result["answer"],
        sources=result["sources"],
    )