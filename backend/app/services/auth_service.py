from sqlalchemy.orm import Session

from app.auth.jwt import create_access_token
from app.auth.password import verify_password
from app.exceptions.auth import (
    InactiveUserError,
    InvalidCredentialsError,
)
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
)


class AuthService:

    def __init__(self):
        self.user_repository = UserRepository()

    def login(
        self,
        db: Session,
        login_request: LoginRequest,
    ) -> TokenResponse:

        user = self.user_repository.get_by_email(
            db,
            login_request.email,
        )

        if user is None:
            raise InvalidCredentialsError()

        if not verify_password(
            login_request.password,
            user.password_hash,
        ):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InactiveUserError()

        access_token = create_access_token(
            str(user.id),
        )

        return TokenResponse(
            access_token=access_token,
        )