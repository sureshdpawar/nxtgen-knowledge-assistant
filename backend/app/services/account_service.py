from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.auth.password import (
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.account import (
    ChangePasswordRequest,
    ChangePasswordResponse,
)


class AccountService:

    def change_password(
        self,
        db: Session,
        current_user: User,
        payload:
            ChangePasswordRequest,
    ) -> ChangePasswordResponse:

        if not verify_password(
            payload.current_password,
            current_user.password_hash,
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Current password "
                    "is incorrect."
                ),
            )

        if verify_password(
            payload.new_password,
            current_user.password_hash,
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    "New password must be "
                    "different from the "
                    "current password."
                ),
            )

        current_user.password_hash = (
            hash_password(
                payload.new_password,
            )
        )

        db.add(
            current_user,
        )

        db.commit()

        db.refresh(
            current_user,
        )

        return ChangePasswordResponse(
            message=(
                "Password changed "
                "successfully."
            ),
        )