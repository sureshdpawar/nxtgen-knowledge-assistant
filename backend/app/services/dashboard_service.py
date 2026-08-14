from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.models.document import (
    Document,
)
from app.models.knowledge_base import (
    KnowledgeBase,
)
from app.models.knowledge_source import (
    KnowledgeSource,
)
from app.models.tenant import (
    Tenant,
)
from app.models.user import (
    User,
)
from app.schemas.dashboard import (
    DashboardStatsResponse,
    PlatformDashboardStatsResponse,
)


class DashboardService:

    def get_admin_stats(
        self,
        db: Session,
        current_user: User,
    ) -> DashboardStatsResponse:

        tenant_id = current_user.tenant_id

        if tenant_id is None:
            return DashboardStatsResponse(
                total_users=0,
                active_users=0,
                knowledge_bases=0,
                knowledge_sources=0,
                documents=0,
            )

        total_users = (
            db.scalar(
                select(
                    func.count(User.id),
                ).where(
                    User.tenant_id
                    == tenant_id,
                )
            )
            or 0
        )

        active_users = (
            db.scalar(
                select(
                    func.count(User.id),
                ).where(
                    User.tenant_id
                    == tenant_id,
                    User.is_active.is_(True),
                )
            )
            or 0
        )

        knowledge_bases = (
            db.scalar(
                select(
                    func.count(
                        KnowledgeBase.id,
                    ),
                ).where(
                    KnowledgeBase.tenant_id
                    == tenant_id,
                )
            )
            or 0
        )

        knowledge_sources = (
            db.scalar(
                select(
                    func.count(
                        KnowledgeSource.id,
                    ),
                )
                .join(
                    KnowledgeBase,
                    KnowledgeBase.id
                    == KnowledgeSource
                    .knowledge_base_id,
                )
                .where(
                    KnowledgeBase.tenant_id
                    == tenant_id,
                )
            )
            or 0
        )

        documents = (
            db.scalar(
                select(
                    func.count(
                        Document.id,
                    ),
                )
                .join(
                    KnowledgeSource,
                    KnowledgeSource.id
                    == Document
                    .knowledge_source_id,
                )
                .join(
                    KnowledgeBase,
                    KnowledgeBase.id
                    == KnowledgeSource
                    .knowledge_base_id,
                )
                .where(
                    KnowledgeBase.tenant_id
                    == tenant_id,
                )
            )
            or 0
        )

        return DashboardStatsResponse(
            total_users=
                int(total_users),

            active_users=
                int(active_users),

            knowledge_bases=
                int(knowledge_bases),

            knowledge_sources=
                int(knowledge_sources),

            documents=
                int(documents),
        )

    def get_platform_stats(
        self,
        db: Session,
    ) -> PlatformDashboardStatsResponse:

        total_tenants = (
            db.scalar(
                select(
                    func.count(
                        Tenant.id,
                    ),
                )
            )
            or 0
        )

        active_tenants = (
            db.scalar(
                select(
                    func.count(
                        Tenant.id,
                    ),
                ).where(
                    Tenant.status
                    == "active",
                )
            )
            or 0
        )

        total_admins = (
            db.scalar(
                select(
                    func.count(
                        User.id,
                    ),
                ).where(
                    User.role
                    == UserRole.ADMIN,
                )
            )
            or 0
        )

        total_users = (
            db.scalar(
                select(
                    func.count(
                        User.id,
                    ),
                ).where(
                    User.role
                    == UserRole.USER,
                )
            )
            or 0
        )

        return (
            PlatformDashboardStatsResponse(
                total_tenants=
                    int(total_tenants),

                active_tenants=
                    int(active_tenants),

                total_admins=
                    int(total_admins),

                total_users=
                    int(total_users),
            )
        )