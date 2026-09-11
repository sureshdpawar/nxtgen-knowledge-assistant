from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Request,
    status,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.auth.permissions import require_authenticated_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.a2a import (
    A2ASendMessageRequest,
    A2ASendMessageResponse,
)
from app.services.a2a_service import A2AService


router = APIRouter(
    prefix="/a2a/agents",
    tags=["A2A"],
)

service = A2AService()


class A2AJSONResponse(JSONResponse):
    media_type = "application/a2a+json"


def _require_v1(version: str | None) -> None:
    if version is None or version.strip() != "1.0":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This Knowgentiq A2A slice supports A2A-Version 1.0.",
        )


@router.get("/{agent_id}/agent-card")
def get_agent_card(
    agent_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    interface_url = str(request.base_url).rstrip("/") + (
        f"/api/v1/a2a/agents/{agent_id}"
    )
    return service.authenticated_agent_card(
        db=db,
        current_user=current_user,
        agent_id=agent_id,
        interface_url=interface_url,
    )


@router.post(
    "/{agent_id}/message:send",
    response_model=A2ASendMessageResponse,
    response_model_by_alias=True,
    response_class=A2AJSONResponse,
)
async def send_message(
    agent_id: UUID,
    payload: A2ASendMessageRequest,
    a2a_version: str | None = Header(
        default=None,
        alias="A2A-Version",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    _require_v1(a2a_version)
    return await service.send_message_authenticated(
        db=db,
        current_user=current_user,
        agent_id=agent_id,
        payload=payload,
    )
