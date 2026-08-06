from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

service = UserService()


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    return service.create(db, user)


@router.get(
    "/",
    response_model=list[UserResponse],
)
def list_users(
    db: Session = Depends(get_db),
):
    return service.list(db)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    return service.get(
        db,
        user_id,
    )


@router.put(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: UUID,
    user: UserUpdate,
    db: Session = Depends(get_db),
):
    return service.update(
        db,
        user_id,
        user,
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    service.delete(
        db,
        user_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )