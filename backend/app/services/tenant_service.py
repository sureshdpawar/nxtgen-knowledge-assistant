from sqlalchemy.orm import Session

from app.models.tenant import Tenant
from app.repositories.tenant_repository import TenantRepository
from app.schemas.tenant import TenantCreate


class TenantService:

    def __init__(self):
        self.repo = TenantRepository()

    def create(self, db: Session, tenant_data: TenantCreate) -> Tenant:

        existing = self.repo.get_by_slug(db, tenant_data.slug)

        if existing:
            raise ValueError("Tenant slug already exists")

        tenant = Tenant(
            name=tenant_data.name,
            slug=tenant_data.slug,
        )

        self.repo.create(db, tenant)

        db.commit()

        db.refresh(tenant)

        return tenant