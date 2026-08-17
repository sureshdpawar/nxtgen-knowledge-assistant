from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from app.auth.dependencies import (
    get_current_active_user,
)
from app.db.session import (
    get_db,
)
from app.models.user import (
    User,
)
from app.schemas.account import (
    ChangePasswordRequest,
    ChangePasswordResponse,
)
from app.services.account_service import (
    AccountService,
)


router = APIRouter(
    prefix="/account",
    tags=[
        "Account",
    ],
)


service = (
    AccountService()
)


@router.put(
    "/change-password",
    response_model=
        ChangePasswordResponse,
)
def change_password(
    payload:
        ChangePasswordRequest,
    db: Session = Depends(
        get_db,
    ),
    current_user: User = Depends(
        get_current_active_user,
    ),
):
    return service.change_password(
        db=db,
        current_user=
            current_user,
        payload=
            payload,
    )