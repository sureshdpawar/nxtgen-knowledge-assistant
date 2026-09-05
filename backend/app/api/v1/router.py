from fastapi import APIRouter

from app.api.v1.routers import account
from app.api.v1.routers import agent
from app.api.v1.routers import agent_access
from app.api.v1.routers import agent_action_approval
from app.api.v1.routers import agent_runs
from app.api.v1.routers import auth
from app.api.v1.routers import chat
from app.api.v1.routers import chat_channel
from app.api.v1.routers import conversation
from app.api.v1.routers import cost_analytics
from app.api.v1.routers import dashboard
from app.api.v1.routers import document
from app.api.v1.routers import eval
from app.api.v1.routers import integration
from app.api.v1.routers import knowledge_base
from app.api.v1.routers import knowledge_source
from app.api.v1.routers import online_eval
from app.api.v1.routers import search
from app.api.v1.routers import tenant
from app.api.v1.routers import (
    tenant_llm_configuration,
)
from app.api.v1.routers import tool_definition
from app.api.v1.routers import trace_debug
from app.api.v1.routers import usage_limit
from app.api.v1.routers import user


api_router = APIRouter()


api_router.include_router(
    auth.router,
)

api_router.include_router(
    tenant.router,
)

api_router.include_router(
    user.router,
)

api_router.include_router(
    knowledge_base.router,
)

api_router.include_router(
    knowledge_source.router,
)

api_router.include_router(
    document.router,
)

api_router.include_router(
    search.router,
)

api_router.include_router(
    chat.router,
)

api_router.include_router(
    chat_channel.router,
)

api_router.include_router(
    tenant_llm_configuration.router,
)

api_router.include_router(
    conversation.router,
)

api_router.include_router(
    dashboard.router,
)

api_router.include_router(
    agent.router,
)

api_router.include_router(
    agent_access.router,
)

api_router.include_router(
    agent_runs.router,
)

api_router.include_router(
    agent_action_approval.router,
)

api_router.include_router(
    integration.router,
)

api_router.include_router(
    tool_definition.router,
)

api_router.include_router(
    account.router,
)

api_router.include_router(
    eval.router,
)

api_router.include_router(
    online_eval.router,
)

api_router.include_router(
    trace_debug.router,
)

api_router.include_router(
    usage_limit.router,
)

api_router.include_router(
    cost_analytics.router,
)
