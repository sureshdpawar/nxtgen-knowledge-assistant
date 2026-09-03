import json

from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    status,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.website_channel import (
    WebsiteChatRequest,
    WebsitePreChatConfig,
    WebsiteSessionRequest,
    WebsiteSessionResponse,
    WebsiteWidgetConfigResponse,
)
from app.services.channel_chat_service import ChannelChatService
from app.services.website_agent_service import WebsiteAgentService
from app.services.website_channel_session_service import (
    WebsiteChannelSessionService,
)


router = APIRouter(
    prefix="/widget",
    tags=["Website Widget"],
)

session_service = WebsiteChannelSessionService()
chat_service = ChannelChatService()
website_agent_service = WebsiteAgentService()


def _sse_text(value: str) -> str:
    return (
        "".join(
            f"data: {line}\n"
            for line in value.split("\n")
        )
        + "\n"
    )


def _sse_event(
    event: str,
    data: dict,
) -> str:
    return (
        f"event: {event}\n"
        f"data: {json.dumps(data)}\n\n"
    )


@router.get(
    "/config/{channel_id}",
    response_model=WebsiteWidgetConfigResponse,
)
def get_widget_config(
    channel_id: UUID,
    origin: str | None = Header(
        default=None,
        alias="Origin",
    ),
    db: Session = Depends(get_db),
):
    try:
        channel = session_service.get_channel(
            db=db,
            channel_id=channel_id,
        )

        session_service.validate_origin(
            channel=channel,
            origin=origin,
        )

        configuration = channel.configuration or {}

        execution_mode = (
            website_agent_service
            .execution_mode(channel)
        )

        if execution_mode == "AGENT":
            pre_chat = (
                website_agent_service
                .public_pre_chat_config(channel)
            )
        else:
            pre_chat = {
                "enabled": False,
                "title": "Before we start",
                "submit_label": "Start chat",
                "fields": [],
            }

        return WebsiteWidgetConfigResponse(
            channel_id=channel.id,
            name=channel.name,
            widget_title=(
                configuration.get("widget_title")
                or channel.name
            ),
            welcome_message=(
                configuration.get("welcome_message")
                or "Hi! How can I help?"
            ),
            placeholder=(
                configuration.get("placeholder")
                or "Ask a question..."
            ),
            show_sources=bool(
                configuration.get(
                    "show_sources",
                    True,
                )
            ),
            execution_mode=execution_mode,
            pre_chat=WebsitePreChatConfig(
                **pre_chat
            ),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.post(
    "/session",
    response_model=WebsiteSessionResponse,
)
async def create_widget_session(
    payload: WebsiteSessionRequest,
    origin: str | None = Header(
        default=None,
        alias="Origin",
    ),
    db: Session = Depends(get_db),
):
    try:
        channel = session_service.get_channel(
            db=db,
            channel_id=payload.channel_id,
        )

        normalized_origin = (
            session_service.validate_origin(
                channel=channel,
                origin=origin,
            )
        )

        runtime_context = {}

        if (
            website_agent_service
            .execution_mode(channel)
            == "AGENT"
        ):
            runtime_context = await (
                website_agent_service
                .start_session(
                    db=db,
                    channel=channel,
                    visitor=payload.visitor,
                )
            )

        (
            token,
            expires_in,
            visitor_id,
            thread_id,
        ) = session_service.create_token(
            channel=channel,
            origin=normalized_origin,
            runtime_context=runtime_context,
        )

        return WebsiteSessionResponse(
            token=token,
            expires_in=expires_in,
            visitor_id=visitor_id,
            thread_id=thread_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post("/chat/stream")
async def widget_chat_stream(
    payload: WebsiteChatRequest,
    authorization: str | None = Header(
        default=None,
        alias="Authorization",
    ),
    origin: str | None = Header(
        default=None,
        alias="Origin",
    ),
    db: Session = Depends(get_db),
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Widget authorization token "
                "is required."
            ),
        )

    scheme, separator, token = (
        authorization.partition(" ")
    )

    if (
        separator != " "
        or scheme.lower() != "bearer"
        or not token.strip()
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid widget authorization.",
        )

    try:
        (
            channel,
            visitor_id,
            thread_id,
            runtime_context,
        ) = session_service.verify_token(
            db=db,
            token=token.strip(),
            origin=origin,
        )

        if (
            website_agent_service
            .execution_mode(channel)
            == "KNOWLEDGE"
        ):
            generator = chat_service.chat_stream(
                db=db,
                tenant_id=channel.tenant_id,
                chat_channel_id=channel.id,
                knowledge_base_id=(
                    channel.knowledge_base_id
                ),
                session_id=payload.session_id,
                query=payload.message,
            )

            return StreamingResponse(
                generator,
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                    "X-NXTGEN-Visitor-ID":
                        visitor_id,
                },
            )

        async def agent_generator(
        ) -> AsyncGenerator[str, None]:
            try:
                result = await (
                    website_agent_service
                    .chat(
                        db=db,
                        channel=channel,
                        visitor_id=visitor_id,
                        thread_id=thread_id,
                        runtime_context=runtime_context,
                        query=payload.message,
                    )
                )

                answer = (
                    result.get("answer")
                    or ""
                )

                if answer:
                    yield _sse_text(answer)

                yield _sse_event(
                    "metadata",
                    {
                        "session_id":
                            str(thread_id),
                        "thread_id":
                            str(thread_id),
                        "run_id":
                            str(result["run_id"]),
                        "sources":
                            [],
                    },
                )

            except Exception:
                yield _sse_event(
                    "error",
                    {
                        "code":
                            "AGENT_EXECUTION_FAILED",
                        "message":
                            (
                                "I couldn't complete "
                                "that request right now. "
                                "Please try again."
                            ),
                    },
                )
            finally:
                yield _sse_event("done", {})

        return StreamingResponse(
            agent_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
                "X-NXTGEN-Visitor-ID":
                    visitor_id,
            },
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
