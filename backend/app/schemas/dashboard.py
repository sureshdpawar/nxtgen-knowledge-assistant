from pydantic import BaseModel


class DashboardStatsResponse(
    BaseModel,
):
    total_users: int
    active_users: int
    knowledge_bases: int
    knowledge_sources: int
    documents: int


class PlatformDashboardStatsResponse(
    BaseModel,
):
    total_tenants: int
    active_tenants: int
    total_admins: int
    total_users: int