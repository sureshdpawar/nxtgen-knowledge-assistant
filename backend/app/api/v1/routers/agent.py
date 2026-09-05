import asyncio
import json

from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Query,
    Response,
    status,
)
from fastapi.responses import (
    StreamingResponse,
)
from sqlalchemy.orm import Session

from app.auth.permissions import (
    require_admin,
    require_authenticated_user,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.agent import (
    AgentCreate,
    AgentResponse,
    AgentUpdate,
)
from app.schemas.agent_run import (
    AgentCheckpointHistoryResponse,
    AgentGraphStateResponse,
    AgentResumeRequest,
    AgentRunRequest,
    AgentRunResponse,
)
from app.services.agent_execution_service import (
    AgentExecutionService,
)
from app.services.agent_service import (
    AgentService,
)


router = APIRouter(
    prefix="/agents",
    tags=["Agents"],
)


service = AgentService()
execution_service = (
    AgentExecutionService()
)


@router.get(
    "",
    response_model=list[
        AgentResponse
    ],
)
def list_agents(
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_authenticated_user,
    ),
):
    return service.list(
        db=db,
        current_user=current_user,
    )


@router.get(
    "/{agent_id}",
    response_model=
        AgentResponse,
)
def get_agent(
    agent_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_authenticated_user,
    ),
):
    return service.get(
        db=db,
        current_user=current_user,
        agent_id=agent_id,
    )


@router.post(
    "",
    response_model=
        AgentResponse,
    status_code=
        status.HTTP_201_CREATED,
)
def create_agent(
    payload: AgentCreate,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    return service.create(
        db=db,
        current_user=current_user,
        payload=payload,
    )


@router.put(
    "/{agent_id}",
    response_model=
        AgentResponse,
)
def update_agent(
    agent_id: UUID,
    payload: AgentUpdate,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    return service.update(
        db=db,
        current_user=current_user,
        agent_id=agent_id,
        payload=payload,
    )


@router.delete(
    "/{agent_id}",
    status_code=
        status.HTTP_204_NO_CONTENT,
)
def delete_agent(
    agent_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    service.delete(
        db=db,
        current_user=current_user,
        agent_id=agent_id,
    )

    return Response(
        status_code=
            status.HTTP_204_NO_CONTENT,
    )


@router.post(
    "/{agent_id}/run",
    response_model=
        AgentRunResponse,
)
async def run_agent(
    agent_id: UUID,
    payload: AgentRunRequest,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_authenticated_user,
    ),
):
    service.get(
        db=db,
        current_user=current_user,
        agent_id=agent_id,
    )

    return await execution_service.run(
        db=db,
        current_user=current_user,
        agent_id=agent_id,
        query=payload.query,
        thread_id=
            payload.thread_id,
    )


@router.post(
    "/{agent_id}/runs/{run_id}/resume",
    response_model=
        AgentRunResponse,
)
async def resume_agent(
    agent_id: UUID,
    run_id: UUID,
    payload: AgentResumeRequest,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_authenticated_user,
    ),
):
    service.get(
        db=db,
        current_user=current_user,
        agent_id=agent_id,
    )

    return await execution_service.resume(
        db=db,
        current_user=current_user,
        agent_id=agent_id,
        run_id=run_id,
        decision=
            payload.decision,
        reason=
            payload.reason,
    )


@router.post(
    "/{agent_id}/run/stream",
)
async def stream_agent(
    agent_id: UUID,
    payload: AgentRunRequest,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_authenticated_user,
    ),
):
    service.get(
        db=db,
        current_user=current_user,
        agent_id=agent_id,
    )

    queue: asyncio.Queue[
        dict | None
    ] = asyncio.Queue()

    async def progress_callback(
        event: dict,
    ):
        await queue.put(
            event,
        )

    async def execute():
        try:
            result = (
                await
                execution_service.run(
                    db=db,
                    current_user=
                        current_user,
                    agent_id=
                        agent_id,
                    query=
                        payload.query,
                    thread_id=
                        payload.thread_id,
                    progress_callback=
                        progress_callback,
                )
            )

            await queue.put(
                {
                    "type":
                        (
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
                        ),

                    "result":
                        result,
                }
            )

        except Exception:
            pass

        finally:
            await queue.put(
                None,
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

                yield (
                    "event: progress\n"
                    "data: "
                    + json.dumps(
                        event,
                        default=str,
                    )
                    + "\n\n"
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
            "X-Accel-Buffering":
                "no",
        },
    )


@router.get(
    "/{agent_id}/threads/{thread_id}/state",
    response_model=AgentGraphStateResponse,
)
async def get_agent_graph_state(
    agent_id: UUID,
    thread_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_authenticated_user
    ),
):
    service.get(
        db=db,
        current_user=current_user,
        agent_id=agent_id,
    )

    return await execution_service.get_graph_state(
        db=db,
        current_user=current_user,
        agent_id=agent_id,
        thread_id=thread_id,
    )


@router.get(
    "/{agent_id}/threads/{thread_id}/checkpoints",
    response_model=AgentCheckpointHistoryResponse,
)
async def get_agent_checkpoint_history(
    agent_id: UUID,
    thread_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_authenticated_user
    ),
):
    service.get(
        db=db,
        current_user=current_user,
        agent_id=agent_id,
    )

    checkpoints = await execution_service.get_checkpoint_history(
        db=db,
        current_user=current_user,
        agent_id=agent_id,
        thread_id=thread_id,
        limit=limit,
    )

    return {
        "thread_id": thread_id,
        "checkpoints": checkpoints,
    }
