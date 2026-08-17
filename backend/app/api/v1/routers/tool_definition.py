from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.auth.permissions import (
    require_admin,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.tool_definition import (
    AgentToolAssignRequest,
    ToolDefinitionCreate,
    ToolDefinitionResponse,
    ToolDefinitionUpdate,
)
from app.services.tool_definition_service import (
    ToolDefinitionService,
)


router = APIRouter(
    tags=["Tools"],
)


service = (
    ToolDefinitionService()
)


@router.get(
    "/tools",
    response_model=list[
        ToolDefinitionResponse
    ],
)
def list_tools(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_admin,
    ),
):
    return service.list(
        db=db,
        current_user=current_user,
    )


@router.post(
    "/tools",
    response_model=
        ToolDefinitionResponse,
    status_code=
        status.HTTP_201_CREATED,
)
def create_tool(
    payload:
        ToolDefinitionCreate,
    db: Session = Depends(get_db),
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
    "/tools/{tool_id}",
    response_model=
        ToolDefinitionResponse,
)
def update_tool(
    tool_id: UUID,
    payload:
        ToolDefinitionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_admin,
    ),
):
    return service.update(
        db=db,
        current_user=current_user,
        tool_id=tool_id,
        payload=payload,
    )


@router.delete(
    "/tools/{tool_id}",
    status_code=
        status.HTTP_204_NO_CONTENT,
)
def delete_tool(
    tool_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_admin,
    ),
):
    service.delete(
        db=db,
        current_user=current_user,
        tool_id=tool_id,
    )

    return Response(
        status_code=
            status.HTTP_204_NO_CONTENT,
    )


@router.put(
    "/agents/{agent_id}/tools",
    response_model=list[
        ToolDefinitionResponse
    ],
)
def assign_agent_tools(
    agent_id: UUID,
    payload:
        AgentToolAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_admin,
    ),
):
    return service.assign_tools(
        db=db,
        current_user=current_user,
        agent_id=agent_id,
        tool_ids=
            payload.tool_ids,
    )