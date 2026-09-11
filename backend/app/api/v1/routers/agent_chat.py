import asyncio
import contextvars
import json

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

from app.auth.permissions import (
    require_authenticated_user,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.agent_chat import (
    AgentChatRequest,
    AgentChatResult,
)
from app.services.agent_chat_service import (
    AgentChatService,
)
from app.services.guardrails_service import (
    GuardrailBlockedError,
    GuardrailsService,
)


router = APIRouter(
    prefix="/agent-chat",
    tags=["Agent Chat"],
)


service = AgentChatService()
guardrails_service = GuardrailsService()


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


async def _guard_input(
    query: str,
) -> str:
    try:
        return (
            await
            guardrails_service
            .check_input_async(
                query
            )
        )
    except GuardrailBlockedError as exc:
        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


async def _guard_result_output(
    result: dict,
) -> dict:
    answer = (
        result.get(
            "answer"
        )
        or ""
    )

    if not answer:
        return result

    guarded_result = dict(
        result
    )

    try:
        guarded_result[
            "answer"
        ] = (
            await
            guardrails_service
            .check_output_async(
                answer
            )
        )
    except GuardrailBlockedError as exc:
        guarded_result[
            "answer"
        ] = str(exc)

    return guarded_result


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
    guarded_query = (
        await
        _guard_input(
            payload.query
        )
    )

    result = (
        await
        service.run(
            db=db,
            current_user=current_user,
            agent_id=
                payload.agent_id,
            conversation_id=
                payload.conversation_id,
            query=
                guarded_query,
        )
    )

    return (
        await
        _guard_result_output(
            result
        )
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
    """
    Stream an Agent Chat turn.

    Important observability detail:

    StreamingResponse executes its body iterator
    after the endpoint function has returned.

    Agent execution is also started inside that
    iterator as an asyncio task. Without explicitly
    preserving the endpoint's contextvars context,
    the OpenTelemetry request span may no longer be
    the current context when Agent execution records
    LLM usage.

    Online Agent evaluation derives its production
    source_trace_id from that LLM usage record. A
    missing trace context therefore causes the
    otherwise-successful Agent RAG interaction to
    be skipped by online-evaluation capture.

    Capture the current context while the FastAPI
    request span is still active and use that exact
    context for the Agent execution task.
    """

    guarded_query = (
        await
        _guard_input(
            payload.query
        )
    )

    queue: asyncio.Queue[
        dict | None
    ] = asyncio.Queue()

    request_context = (
        contextvars.copy_context()
    )

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
                    guarded_query,
                progress_callback=
                    progress_callback,
            )

            result = (
                await
                _guard_result_output(
                    result
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
            execute(),
            context=
                request_context,
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
