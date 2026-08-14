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
from app.schemas.knowledge_base import (
    KnowledgeBaseResponse,
)
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.services.knowledge_base_access_service import (
    KnowledgeBaseAccessService,
)
from app.services.user_service import (
    UserService,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


service = UserService()

access_service = (
    KnowledgeBaseAccessService()
)


@router.get(
    "/",
    response_model=list[
        UserResponse
    ],
)
def list_users(
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
    "/{user_id}/knowledge-bases",
    response_model=list[
        KnowledgeBaseResponse
    ],
)
def list_user_knowledge_bases(
    user_id: UUID,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        require_admin,
    ),
):
    return (
        access_service
        .list_for_user(
            db=db,
            current_user=current_user,
            user_id=user_id,
        )
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: UUID,
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
        user_id=user_id,
    )


@router.post(
    "/",
    response_model=
        UserResponse,
    status_code=
        status.HTTP_201_CREATED,
)
def create_user(
    user: UserCreate,
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
        user_create=user,
    )


@router.put(
    "/{user_id}",
    response_model=
        UserResponse,
)
def update_user(
    user_id: UUID,
    user: UserUpdate,
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
        user_id=user_id,
        user_update=user,
    )


@router.delete(
    "/{user_id}",
    status_code=
        status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: UUID,
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
        user_id=user_id,
    )

    return Response(
        status_code=
            status.HTTP_204_NO_CONTENT,
    )