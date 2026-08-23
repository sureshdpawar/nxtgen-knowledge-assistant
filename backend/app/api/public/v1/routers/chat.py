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
from app.api.public.deps import (
    get_public_chat_channel,
)
from app.models.chat_channel import (
    ChatChannel,
)
from app.schemas.public_channel_chat import (
    PublicChannelChatRequest,
    PublicChannelChatResponse,
)
from app.services.channel_chat_service import (
    ChannelChatService,
)


router = APIRouter(
    prefix="/chat",
    tags=[
        "Public Chat API"
    ],
)


service = (
    ChannelChatService()
)


@router.post(
    "",
    response_model=(
        PublicChannelChatResponse
    ),
)
def chat(
    payload:
        PublicChannelChatRequest,

    db: Session = Depends(
        get_db
    ),

    channel: ChatChannel = Depends(
        get_public_chat_channel
    ),
):
    try:
        result = service.chat(
            db=db,
            tenant_id=(
                channel.tenant_id
            ),
            chat_channel_id=(
                channel.id
            ),
            knowledge_base_id=(
                channel.knowledge_base_id
            ),
            session_id=(
                payload.session_id
            ),
            query=(
                payload.message
            ),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(
                exc
            ),
        ) from exc

    return (
        PublicChannelChatResponse(
            session_id=(
                result[
                    "session_id"
                ]
            ),
            answer=(
                result[
                    "answer"
                ]
            ),
            sources=(
                result[
                    "sources"
                ]
            ),
        )
    )


@router.post(
    "/stream",
)
def chat_stream(
    payload:
        PublicChannelChatRequest,

    db: Session = Depends(
        get_db
    ),

    channel: ChatChannel = Depends(
        get_public_chat_channel
    ),
):
    try:
        generator = (
            service.chat_stream(
                db=db,
                tenant_id=(
                    channel.tenant_id
                ),
                chat_channel_id=(
                    channel.id
                ),
                knowledge_base_id=(
                    channel
                    .knowledge_base_id
                ),
                session_id=(
                    payload.session_id
                ),
                query=(
                    payload.message
                ),
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(
                exc
            ),
        ) from exc

    return StreamingResponse(
        generator,
        media_type=(
            "text/event-stream"
        ),
        headers={
            "Cache-Control":
                "no-cache",

            "Connection":
                "keep-alive",

            "X-Accel-Buffering":
                "no",
        },
    )