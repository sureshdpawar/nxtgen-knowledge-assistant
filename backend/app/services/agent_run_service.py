from uuid import UUID

from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.models.agent_run import (
    AgentRun,
)
from app.models.user import User
from app.repositories.agent_run_repository import (
    AgentRunRepository,
)


class AgentRunService:

    def __init__(self):
        self.repository = (
            AgentRunRepository()
        )

    def list_for_agent(
        self,
        db: Session,
        current_user: User,
        agent_id: UUID,
    ) -> list[AgentRun]:

        return (
            self.repository
            .list_by_agent(
                db=db,
                tenant_id=
                    current_user.tenant_id,
                agent_id=
                    agent_id,
            )
        )

    def get(
        self,
        db: Session,
        current_user: User,
        run_id: UUID,
    ) -> AgentRun:

        run = (
            self.repository
            .get_by_id_and_tenant(
                db=db,
                tenant_id=
                    current_user.tenant_id,
                run_id=
                    run_id,
            )
        )

        if run is None:
            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,
                detail=(
                    "Agent run not found."
                ),
            )

        return run