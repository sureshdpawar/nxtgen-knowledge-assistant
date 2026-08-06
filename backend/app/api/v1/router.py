from fastapi import APIRouter

from app.api.v1.routers import tenant

api_router = APIRouter()

api_router.include_router(
    tenant.router,
)