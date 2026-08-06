from uuid import UUID

from sqlalchemy.orm import Session

from app.models.tenant import Tenant
from app.repositories.tenant_repository import TenantRepository
from app.schemas.tenant import TenantCreate
from app.schemas.tenant import TenantUpdate
from app.exceptions.tenant import TenantNotFoundError
from app.exceptions.tenant import DuplicateTenantSlugError

class TenantService:

    def __init__(self):
        self.repo = TenantRepository()

    def list(self, db: Session) -> list[Tenant]:
        return self.repo.list(db)

    def get(self, db: Session, tenant_id: UUID) -> Tenant:

        tenant = self.repo.get(db, tenant_id)

        if tenant is None:
            raise TenantNotFoundError()

        return tenant

    def create(self, db: Session, tenant_data: TenantCreate) -> Tenant:

        existing = self.repo.get_by_slug(db, tenant_data.slug)

        if existing:
            raise DuplicateTenantSlugError()

        tenant = Tenant(
            name=tenant_data.name,
            slug=tenant_data.slug,
        )

        self.repo.create(db, tenant)

        db.commit()

        db.refresh(tenant)

        return tenant
    
    def update(
        self,
        db: Session,
        tenant_id: UUID,
        tenant_data: TenantUpdate,
    ) -> Tenant:

        tenant = self.get(db, tenant_id)

        if tenant_data.name is not None:
            tenant.name = tenant_data.name

        if tenant_data.plan is not None:
            tenant.plan = tenant_data.plan

        if tenant_data.status is not None:
            tenant.status = tenant_data.status

        db.commit()
        db.refresh(tenant)

        return tenant
    
    def delete(
        self,
        db: Session,
        tenant_id: UUID,
    ) -> None:

        tenant = self.get(db, tenant_id)

        self.repo.delete(db, tenant)

        db.commit()