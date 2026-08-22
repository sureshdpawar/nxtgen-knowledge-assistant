from fastapi import (
    APIRouter,
)

from app.api.public.v1.routers import (
    chat,
    slack,
    widget,
)


public_api_router = (
    APIRouter()
)


public_api_router.include_router(
    chat.router,
)

public_api_router.include_router(
    widget.router,
)

public_api_router.include_router(
    slack.router,
)