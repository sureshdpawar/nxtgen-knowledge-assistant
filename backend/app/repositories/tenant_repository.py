from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tenant import Tenant


class TenantRepository:

    def get(self, db: Session, tenant_id: UUID) -> Tenant | None:
        return db.get(Tenant, tenant_id)

    def get_by_slug(self, db: Session, slug: str) -> Tenant | None:
        stmt = select(Tenant).where(Tenant.slug == slug)
        return db.execute(stmt).scalar_one_or_none()

    def list(self, db: Session) -> list[Tenant]:
        stmt = select(Tenant)
        return db.execute(stmt).scalars().all()

    def create(self, db: Session, tenant: Tenant) -> Tenant:
        db.add(tenant)
        db.flush()
        db.refresh(tenant)
        return tenant

    def delete(self, db: Session, tenant: Tenant):
        db.delete(tenant)