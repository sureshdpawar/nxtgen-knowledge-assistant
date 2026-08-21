from fastapi import (
    Depends,
    Header,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.chat_channel import (
    ChatChannel,
)
from app.services.chat_channel_service import (
    ChatChannelService,
)


channel_service = (
    ChatChannelService()
)


def get_public_chat_channel(
    authorization: str | None = Header(
        default=None,
        alias="Authorization",
    ),
    db: Session = Depends(
        get_db
    ),
) -> ChatChannel:
    if authorization is None:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Authorization header "
                "is required."
            ),
            headers={
                "WWW-Authenticate":
                    "Bearer",
            },
        )

    scheme, separator, token = (
        authorization.partition(
            " "
        )
    )

    if (
        separator != " "
        or scheme.lower()
        != "bearer"
        or not token.strip()
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Authorization must use "
                "Bearer authentication."
            ),
            headers={
                "WWW-Authenticate":
                    "Bearer",
            },
        )

    try:
        return (
            channel_service
            .authenticate_api_key(
                db=db,
                api_key=(
                    token.strip()
                ),
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Invalid or inactive "
                "API key."
            ),
            headers={
                "WWW-Authenticate":
                    "Bearer",
            },
        ) from exc