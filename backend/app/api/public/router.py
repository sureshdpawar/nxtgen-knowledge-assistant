from fastapi import APIRouter

from app.api.public.v1.routers import (
    chat,
)


public_api_router = (
    APIRouter()
)


public_api_router.include_router(
    chat.router
)