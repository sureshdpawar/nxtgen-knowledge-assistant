from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    status,
)
from fastapi.responses import (
    StreamingResponse,
)
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.website_channel import (
    WebsiteChatRequest,
    WebsiteSessionRequest,
    WebsiteSessionResponse,
    WebsiteWidgetConfigResponse,
)
from app.services.channel_chat_service import (
    ChannelChatService,
)
from app.services.website_channel_session_service import (
    WebsiteChannelSessionService,
)


router = APIRouter(
    prefix="/widget",
    tags=[
        "Website Widget"
    ],
)


session_service = (
    WebsiteChannelSessionService()
)

chat_service = (
    ChannelChatService()
)


@router.get(
    "/config/{channel_id}",
    response_model=(
        WebsiteWidgetConfigResponse
    ),
)
def get_widget_config(
    channel_id: UUID,

    origin: str | None = Header(
        default=None,
        alias="Origin",
    ),

    db: Session = Depends(
        get_db
    ),
):
    try:
        channel = (
            session_service
            .get_channel(
                db=db,
                channel_id=channel_id,
            )
        )

        session_service.validate_origin(
            channel=channel,
            origin=origin,
        )

        configuration = (
            channel.configuration
            or {}
        )

        return (
            WebsiteWidgetConfigResponse(
                channel_id=(
                    channel.id
                ),
                name=(
                    channel.name
                ),
                widget_title=(
                    configuration.get(
                        "widget_title"
                    )
                    or channel.name
                ),
                welcome_message=(
                    configuration.get(
                        "welcome_message"
                    )
                    or (
                        "Hi! How can I help?"
                    )
                ),
                placeholder=(
                    configuration.get(
                        "placeholder"
                    )
                    or (
                        "Ask a question..."
                    )
                ),
                show_sources=bool(
                    configuration.get(
                        "show_sources",
                        True,
                    )
                ),
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=str(
                exc
            ),
        ) from exc


@router.post(
    "/session",
    response_model=(
        WebsiteSessionResponse
    ),
)
def create_widget_session(
    payload:
        WebsiteSessionRequest,

    origin: str | None = Header(
        default=None,
        alias="Origin",
    ),

    db: Session = Depends(
        get_db
    ),
):
    try:
        channel = (
            session_service
            .get_channel(
                db=db,
                channel_id=(
                    payload.channel_id
                ),
            )
        )

        normalized_origin = (
            session_service
            .validate_origin(
                channel=channel,
                origin=origin,
            )
        )

        (
            token,
            expires_in,
            visitor_id,
        ) = (
            session_service
            .create_token(
                channel=channel,
                origin=(
                    normalized_origin
                ),
            )
        )

        return (
            WebsiteSessionResponse(
                token=token,
                expires_in=(
                    expires_in
                ),
                visitor_id=(
                    visitor_id
                ),
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=str(
                exc
            ),
        ) from exc


@router.post(
    "/chat/stream",
)
def widget_chat_stream(
    payload:
        WebsiteChatRequest,

    authorization:
        str | None = Header(
            default=None,
            alias="Authorization",
        ),

    origin: str | None = Header(
        default=None,
        alias="Origin",
    ),

    db: Session = Depends(
        get_db
    ),
):
    if not authorization:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Widget authorization "
                "token is required."
            ),
        )

    (
        scheme,
        separator,
        token,
    ) = authorization.partition(
        " "
    )

    if (
        separator != " "
        or scheme.lower()
        != "bearer"
        or not token.strip()
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Invalid widget "
                "authorization."
            ),
        )

    try:
        (
            channel,
            visitor_id,
        ) = (
            session_service
            .verify_token(
                db=db,
                token=(
                    token.strip()
                ),
                origin=origin,
            )
        )

        generator = (
            chat_service
            .chat_stream(
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
                status.HTTP_403_FORBIDDEN
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

            "X-NXTGEN-Visitor-ID":
                visitor_id,
        },
    )