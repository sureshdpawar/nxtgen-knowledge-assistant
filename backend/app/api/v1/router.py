from fastapi import APIRouter

from app.api.v1.routers import auth
from app.api.v1.routers import knowledge_base
from app.api.v1.routers import knowledge_source
from app.api.v1.routers import tenant
from app.api.v1.routers import user
from app.api.v1.routers import document
from app.api.v1.routers import search
from app.api.v1.routers import chat

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(tenant.router)
api_router.include_router(user.router)
api_router.include_router(knowledge_base.router)
api_router.include_router(knowledge_source.router)
api_router.include_router(document.router)
api_router.include_router(search.router,)
api_router.include_router(chat.router,)