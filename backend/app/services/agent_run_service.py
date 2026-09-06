from uuid import UUID

from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.agent_action_approval import (
    AgentActionApproval,
)
from app.models.agent_run import (
    AgentRun,
)
from app.models.user import User
from app.repositories.agent_run_repository import (
    AgentRunRepository,
)
from app.services.llm_usage_service import (
    LLMUsageService,
)


class AgentRunService:

    def __init__(self):
        self.repository = (
            AgentRunRepository()
        )

        self.llm_usage_service = (
            LLMUsageService()
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

        usage = (
            self.llm_usage_service
            .get_agent_run_usage(
                db=db,
                tenant_id=
                    current_user.tenant_id,
                run_id=
                    run.id,
            )
        )

        approvals = list(
            db.scalars(
                select(
                    AgentActionApproval
                )
                .where(
                    AgentActionApproval.tenant_id
                    == current_user.tenant_id,
                    AgentActionApproval.agent_run_id
                    == run.id,
                )
                .order_by(
                    AgentActionApproval.requested_at.asc(),
                    AgentActionApproval.created_at.asc(),
                )
            ).all()
        )

        #
        # Read-model enrichment only.
        #
        # Token/cost data remains owned by
        # LLMUsageEvent rather than being
        # duplicated into AgentRun.
        #
        # Approval data remains owned by
        # AgentActionApproval. Run details
        # expose it as read-only governance
        # evidence so the execution audit is
        # understandable in one place.
        #
        run.usage = usage
        run.approvals = approvals

        return run
