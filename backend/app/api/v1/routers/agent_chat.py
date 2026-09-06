import asyncio
import json

from fastapi import (
    APIRouter,
    Depends,
)
from fastapi.responses import (
    StreamingResponse,
)
from sqlalchemy.orm import Session

from app.auth.permissions import (
    require_authenticated_user,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.agent_chat import (
    AgentChatRequest,
    AgentChatResumeRequest,
    AgentChatResult,
)
from app.services.agent_chat_service import (
    AgentChatService,
)


router = APIRouter(
    prefix="/agent-chat",
    tags=["Agent Chat"],
)


service = AgentChatService()


def _sse(
    event_name: str,
    payload: dict,
) -> str:
    return (
        f"event: {event_name}\n"
        "data: "
        + json.dumps(
            payload,
            default=str,
        )
        + "\n\n"
    )


@router.post(
    "",
    response_model=
        AgentChatResult,
)
async def run_agent_chat(
    payload: AgentChatRequest,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_authenticated_user,
    ),
):
    return await service.run(
        db=db,
        current_user=current_user,
        agent_id=
            payload.agent_id,
        conversation_id=
            payload.conversation_id,
        query=
            payload.query,
    )


@router.post(
    "/resume",
    response_model=
        AgentChatResult,
)
async def resume_agent_chat(
    payload: AgentChatResumeRequest,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_authenticated_user,
    ),
):
    return await service.resume(
        db=db,
        current_user=current_user,
        conversation_id=
            payload.conversation_id,
        run_id=
            payload.run_id,
        decision=
            payload.decision,
        reason=
            payload.reason,
    )


@router.post(
    "/stream",
)
async def stream_agent_chat(
    payload: AgentChatRequest,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_authenticated_user,
    ),
):
    queue: asyncio.Queue[
        dict | None
    ] = asyncio.Queue()

    async def progress_callback(
        event: dict,
    ) -> None:
        await queue.put(
            {
                "event":
                    "progress",
                "data":
                    event,
            }
        )

    async def execute() -> None:
        try:
            result = await service.run(
                db=db,
                current_user=
                    current_user,
                agent_id=
                    payload.agent_id,
                conversation_id=
                    payload
                    .conversation_id,
                query=
                    payload.query,
                progress_callback=
                    progress_callback,
            )

            event_name = (
                "approval_required"
                if (
                    result[
                        "status"
                    ].value
                    ==
                    "WAITING_FOR_APPROVAL"
                )
                else
                "completed"
            )

            await queue.put(
                {
                    "event":
                        event_name,
                    "data":
                        result,
                }
            )

        except Exception as exc:
            await queue.put(
                {
                    "event":
                        "error",
                    "data": {
                        "message":
                            str(exc),
                    },
                }
            )

        finally:
            await queue.put(
                None
            )

    async def event_stream():
        task = asyncio.create_task(
            execute()
        )

        try:
            while True:
                event = (
                    await queue.get()
                )

                if event is None:
                    break

                yield _sse(
                    event[
                        "event"
                    ],
                    event[
                        "data"
                    ],
                )

        finally:
            if task.done():
                try:
                    task.result()
                except Exception:
                    pass

    return StreamingResponse(
        event_stream(),
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


@router.post(
    "/resume/stream",
)
async def stream_agent_chat_resume(
    payload: AgentChatResumeRequest,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_authenticated_user,
    ),
):
    queue: asyncio.Queue[
        dict | None
    ] = asyncio.Queue()

    async def progress_callback(
        event: dict,
    ) -> None:
        await queue.put(
            {
                "event":
                    "progress",
                "data":
                    event,
            }
        )

    async def execute() -> None:
        try:
            result = (
                await service.resume(
                    db=db,
                    current_user=
                        current_user,
                    conversation_id=
                        payload
                        .conversation_id,
                    run_id=
                        payload.run_id,
                    decision=
                        payload.decision,
                    reason=
                        payload.reason,
                    progress_callback=
                        progress_callback,
                )
            )

            event_name = (
                "approval_required"
                if (
                    result[
                        "status"
                    ].value
                    ==
                    "WAITING_FOR_APPROVAL"
                )
                else
                "completed"
            )

            await queue.put(
                {
                    "event":
                        event_name,
                    "data":
                        result,
                }
            )

        except Exception as exc:
            await queue.put(
                {
                    "event":
                        "error",
                    "data": {
                        "message":
                            str(exc),
                    },
                }
            )

        finally:
            await queue.put(
                None
            )

    async def event_stream():
        task = asyncio.create_task(
            execute()
        )

        try:
            while True:
                event = (
                    await queue.get()
                )

                if event is None:
                    break

                yield _sse(
                    event[
                        "event"
                    ],
                    event[
                        "data"
                    ],
                )

        finally:
            if task.done():
                try:
                    task.result()
                except Exception:
                    pass

    return StreamingResponse(
        event_stream(),
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
