from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.jwt import decode_access_token
from app.db.session import get_db
from app.exceptions.auth import (
    InactiveUserError,
    InvalidCredentialsError,
)
from app.repositories.user_repository import UserRepository

security = HTTPBearer()

user_repository = UserRepository()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    try:
        payload = decode_access_token(token)
        user_id = payload["sub"]
    except Exception:
        raise InvalidCredentialsError()

    user = user_repository.get(
        db,
        user_id,
    )

    if user is None:
        raise InvalidCredentialsError()

    return user


def get_current_active_user(
    current_user=Depends(get_current_user),
):
    if not current_user.is_active:
        raise InactiveUserError()

    return current_user