from fastapi import APIRouter

from app.api.health import (
    router as health_router,
)
from app.api.public.v1.router import (
    public_api_router,
)
from app.api.v1.router import (
    api_router,
)


router = APIRouter()


router.include_router(
    health_router,
)


router.include_router(
    api_router,
    prefix="/api/v1",
)


router.include_router(
    public_api_router,
    prefix="/public/v1",
)