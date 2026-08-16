from uuid import UUID

from sqlalchemy import (
    select,
)
from sqlalchemy.orm import (
    Session,
    selectinload,
)

from app.models.agent_run import (
    AgentRun,
)
from app.repositories.base_repository import (
    BaseRepository,
)


class AgentRunRepository(
    BaseRepository[AgentRun],
):

    def __init__(self):
        super().__init__(
            AgentRun,
        )

    def list_by_agent(
        self,
        db: Session,
        tenant_id: UUID,
        agent_id: UUID,
    ) -> list[AgentRun]:

        stmt = (
            select(
                AgentRun,
            )
            .where(
                AgentRun.tenant_id
                == tenant_id,

                AgentRun.agent_id
                == agent_id,
            )
            .order_by(
                AgentRun
                .started_at
                .desc(),
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
        run_id: UUID,
    ) -> AgentRun | None:

        stmt = (
            select(
                AgentRun,
            )
            .options(
                selectinload(
                    AgentRun.steps,
                )
            )
            .where(
                AgentRun.id
                == run_id,

                AgentRun.tenant_id
                == tenant_id,
            )
        )

        return (
            db.scalars(
                stmt,
            )
            .first()
        )