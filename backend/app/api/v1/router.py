from fastapi import APIRouter

from app.api.v1.routers import auth
from app.api.v1.routers import knowledge_base
from app.api.v1.routers import knowledge_source
from app.api.v1.routers import tenant
from app.api.v1.routers import user
from app.api.v1.routers import document
from app.api.v1.routers import search
from app.api.v1.routers import chat
from app.api.v1.routers import (tenant_llm_configuration)
from app.api.v1.routers import conversation
from app.api.v1.routers import dashboard
from app.api.v1.routers import agent
from app.api.v1.routers import (agent_runs,)
from app.api.v1.routers import integration
from app.api.v1.routers import tool_definition

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(tenant.router)
api_router.include_router(user.router)
api_router.include_router(knowledge_base.router)
api_router.include_router(knowledge_source.router)
api_router.include_router(document.router)
api_router.include_router(search.router,)
api_router.include_router(chat.router,)
api_router.include_router(tenant_llm_configuration.router,)
api_router.include_router(conversation.router,)
api_router.include_router(dashboard.router,)
api_router.include_router(agent.router,)
api_router.include_router(agent_runs.router,)
api_router.include_router(integration.router,)
api_router.include_router(tool_definition.router,)