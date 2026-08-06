from fastapi import APIRouter

from app.api.v1.routers import tenant
from app.api.v1.routers import user

api_router = APIRouter()

api_router.include_router(tenant.router)
api_router.include_router(user.router)