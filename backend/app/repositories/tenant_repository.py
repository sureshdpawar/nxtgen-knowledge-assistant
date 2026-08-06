from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tenant import Tenant
from app.repositories.base_repository import BaseRepository


class TenantRepository(BaseRepository[Tenant]):

    def __init__(self):
        super().__init__(Tenant)

    def get_by_slug(
        self,
        db: Session,
        slug: str,
    ) -> Tenant | None:

        stmt = select(Tenant).where(Tenant.slug == slug)

        return db.execute(stmt).scalar_one_or_none()