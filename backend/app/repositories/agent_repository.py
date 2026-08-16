from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import (
    Session,
    selectinload,
)

from app.models.agent import Agent
from app.repositories.base_repository import (
    BaseRepository,
)


class AgentRepository(
    BaseRepository[Agent],
):

    def __init__(self):
        super().__init__(
            Agent,
        )

    def list_by_tenant(
        self,
        db: Session,
        tenant_id: UUID,
    ) -> list[Agent]:

        stmt = (
            select(
                Agent,
            )
            .options(
                selectinload(
                    Agent
                    .knowledge_base_links
                )
            )
            .where(
                Agent.tenant_id
                == tenant_id,
            )
            .order_by(
                Agent.created_at.desc(),
            )
        )

        return list(
            db.scalars(
                stmt,
            ).all()
        )

    def get_by_id_and_tenant(
        self,
        db: Session,
        tenant_id: UUID,
        agent_id: UUID,
    ) -> Agent | None:

        stmt = (
            select(
                Agent,
            )
            .options(
                selectinload(
                    Agent
                    .knowledge_base_links
                )
            )
            .where(
                Agent.id
                == agent_id,

                Agent.tenant_id
                == tenant_id,
            )
        )

        return (
            db.scalars(
                stmt,
            )
            .first()
        )