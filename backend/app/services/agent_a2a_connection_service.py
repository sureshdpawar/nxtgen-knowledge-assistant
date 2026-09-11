from __future__ import annotations

from uuid import UUID

from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy import (
    delete,
    select,
)
from sqlalchemy.orm import Session

from app.core.enums import AgentStatus
from app.models.agent import Agent
from app.models.agent_a2a_connection import (
    AgentA2AConnection,
)
from app.models.user import User
from app.services.agent_access_service import (
    AgentAccessService,
)


class AgentA2AConnectionService:
    def __init__(self):
        self.access_service = AgentAccessService()

    def _source_agent(
        self,
        *,
        db: Session,
        current_user: User,
        agent_id: UUID,
    ) -> Agent:
        return self.access_service.require_agent_access(
            db=db,
            current_user=current_user,
            agent_id=agent_id,
        )

    def list(
        self,
        *,
        db: Session,
        current_user: User,
        agent_id: UUID,
    ) -> list[dict]:
        source = self._source_agent(
            db=db,
            current_user=current_user,
            agent_id=agent_id,
        )

        stmt = (
            select(Agent)
            .join(
                AgentA2AConnection,
                AgentA2AConnection.target_agent_id
                == Agent.id,
            )
            .where(
                AgentA2AConnection.tenant_id
                == source.tenant_id,
                AgentA2AConnection.source_agent_id
                == source.id,
            )
            .order_by(Agent.name.asc())
        )

        targets = list(
            db.scalars(stmt).all()
        )

        return [
            {
                "target_agent_id": target.id,
                "target_agent_name": target.name,
                "target_agent_description": target.description,
                "target_agent_status": target.status.value,
                "protocol": "A2A",
                "protocol_version": "1.0",
            }
            for target in targets
        ]

    def replace(
        self,
        *,
        db: Session,
        current_user: User,
        agent_id: UUID,
        target_agent_ids: list[UUID],
    ) -> list[dict]:
        source = self._source_agent(
            db=db,
            current_user=current_user,
            agent_id=agent_id,
        )

        unique_ids = list(
            dict.fromkeys(target_agent_ids)
        )

        if source.id in unique_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An agent cannot connect to itself.",
            )

        if unique_ids:
            stmt = select(Agent).where(
                Agent.id.in_(unique_ids),
                Agent.tenant_id == source.tenant_id,
            )
            targets = list(
                db.scalars(stmt).all()
            )

            if len(targets) != len(unique_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more connected agents are invalid.",
                )

            inactive = [
                target.name
                for target in targets
                if target.status != AgentStatus.ACTIVE
            ]
            if inactive:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Connected agents must be ACTIVE: "
                        + ", ".join(inactive)
                    ),
                )

        db.execute(
            delete(AgentA2AConnection).where(
                AgentA2AConnection.tenant_id
                == source.tenant_id,
                AgentA2AConnection.source_agent_id
                == source.id,
            )
        )

        for target_id in unique_ids:
            db.add(
                AgentA2AConnection(
                    tenant_id=source.tenant_id,
                    source_agent_id=source.id,
                    target_agent_id=target_id,
                    created_by=current_user.id,
                )
            )

        db.commit()

        return self.list(
            db=db,
            current_user=current_user,
            agent_id=agent_id,
        )
