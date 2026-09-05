from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.enums import (
    AgentActionApprovalStatus,
)
from app.models.agent_action_approval import (
    AgentActionApproval,
)
from app.models.user import User
from app.services.agent_execution_service import (
    AgentExecutionService,
)


class AgentActionApprovalService:

    def __init__(self):
        self.execution_service = (
            AgentExecutionService()
        )

    def _query(self):
        return (
            select(
                AgentActionApproval
            )
            .options(
                joinedload(
                    AgentActionApproval
                    .agent
                ),
                joinedload(
                    AgentActionApproval
                    .run
                ),
            )
        )

    def _get_for_admin(
        self,
        db: Session,
        *,
        current_user: User,
        approval_id: UUID,
    ) -> AgentActionApproval:
        approval = db.scalar(
            self._query()
            .where(
                AgentActionApproval.id
                == approval_id,
                AgentActionApproval
                .tenant_id
                == current_user.tenant_id,
            )
        )

        if approval is None:
            raise HTTPException(
                status_code=(
                    status.HTTP_404_NOT_FOUND
                ),
                detail=(
                    "Agent action approval "
                    "not found."
                ),
            )

        return approval

    def _serialize(
        self,
        approval:
            AgentActionApproval,
    ) -> dict:
        run = approval.run
        agent = approval.agent

        return {
            "id":
                approval.id,
            "tenant_id":
                approval.tenant_id,
            "agent_id":
                approval.agent_id,
            "agent_run_id":
                approval.agent_run_id,
            "checkpoint_id":
                approval.checkpoint_id,
            "actions":
                approval.actions
                or [],
            "status":
                approval.status,
            "requested_at":
                approval.requested_at,
            "decided_at":
                approval.decided_at,
            "decided_by_user_id":
                approval
                .decided_by_user_id,
            "decision_reason":
                approval
                .decision_reason,
            "created_at":
                approval.created_at,
            "updated_at":
                approval.updated_at,
            "agent_name":
                agent.name,
            "actor_type":
                run.actor_type,
            "actor_id":
                run.actor_id,
            "run_query":
                run.query,
            "run_status":
                run.status,
        }

    def list(
        self,
        db: Session,
        *,
        current_user: User,
        approval_status:
            AgentActionApprovalStatus
            | None = None,
    ) -> list[dict]:
        stmt = (
            self._query()
            .where(
                AgentActionApproval
                .tenant_id
                == current_user.tenant_id
            )
        )

        if approval_status is not None:
            stmt = stmt.where(
                AgentActionApproval
                .status
                == approval_status
            )

        stmt = stmt.order_by(
            AgentActionApproval
            .requested_at
            .desc()
        )

        approvals = list(
            db.scalars(
                stmt
            ).all()
        )

        return [
            self._serialize(
                approval
            )
            for approval
            in approvals
        ]

    def get(
        self,
        db: Session,
        *,
        current_user: User,
        approval_id: UUID,
    ) -> dict:
        approval = (
            self._get_for_admin(
                db,
                current_user=
                    current_user,
                approval_id=
                    approval_id,
            )
        )

        return self._serialize(
            approval
        )

    async def approve(
        self,
        db: Session,
        *,
        current_user: User,
        approval_id: UUID,
        reason: str | None,
    ) -> dict:
        return await self._decide(
            db,
            current_user=
                current_user,
            approval_id=
                approval_id,
            decision="approve",
            reason=reason,
        )

    async def reject(
        self,
        db: Session,
        *,
        current_user: User,
        approval_id: UUID,
        reason: str | None,
    ) -> dict:
        return await self._decide(
            db,
            current_user=
                current_user,
            approval_id=
                approval_id,
            decision="reject",
            reason=reason,
        )

    async def _decide(
        self,
        db: Session,
        *,
        current_user: User,
        approval_id: UUID,
        decision: str,
        reason: str | None,
    ) -> dict:
        approval = (
            self._get_for_admin(
                db,
                current_user=
                    current_user,
                approval_id=
                    approval_id,
            )
        )

        if (
            approval.status
            != AgentActionApprovalStatus
            .PENDING
        ):
            raise HTTPException(
                status_code=(
                    status.HTTP_409_CONFLICT
                ),
                detail=(
                    "Agent action approval "
                    "has already been decided."
                ),
            )

        resolved_status = (
            AgentActionApprovalStatus
            .APPROVED
            if decision == "approve"
            else
            AgentActionApprovalStatus
            .REJECTED
        )

        # Persist the governance decision before resuming the
        # external LangGraph checkpoint. If execution later fails,
        # the recorded fact remains truthful: the Admin approved
        # or rejected the proposed action, while execution failed.
        approval.status = (
            resolved_status
        )
        approval.decided_at = (
            datetime.now(
                timezone.utc,
            )
        )
        approval.decided_by_user_id = (
            current_user.id
        )
        approval.decision_reason = (
            reason
        )

        db.commit()

        await (
            self.execution_service
            .resume_for_action_approval(
                db=db,
                tenant_id=
                    current_user.tenant_id,
                run_id=
                    approval.agent_run_id,
                decision=
                    decision,
                reason=
                    reason,
            )
        )

        refreshed = (
            self._get_for_admin(
                db,
                current_user=
                    current_user,
                approval_id=
                    approval_id,
            )
        )

        return self._serialize(
            refreshed
        )
