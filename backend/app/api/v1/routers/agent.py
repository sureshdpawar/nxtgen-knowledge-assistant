import asyncio
import json

from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)
from fastapi.responses import (
    StreamingResponse,
)
from sqlalchemy.orm import Session

from app.auth.permissions import (
    require_admin,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.agent import (
    AgentCreate,
    AgentResponse,
    AgentUpdate,
)
from app.schemas.agent_run import (
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
        require_admin,
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
        require_admin,
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
        require_admin,
    ),
):
    return await execution_service.run(
        db=db,
        current_user=current_user,
        agent_id=agent_id,
        query=payload.query,
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
        require_admin,
    ),
):
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
            await execution_service.run(
                db=db,
                current_user=
                    current_user,
                agent_id=
                    agent_id,
                query=
                    payload.query,
                progress_callback=
                    progress_callback,
            )

        except Exception:
            #
            # AgentExecutionService already
            # emitted a safe failed event
            # and persisted the failed run.
            #
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

                payload_json = (
                    json.dumps(
                        event,
                        default=str,
                    )
                )

                yield (
                    "event: progress\n"
                    f"data: {payload_json}\n\n"
                )

        finally:
            #
            # We intentionally do not cancel
            # an already-running agent if the
            # browser disconnects.
            #
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