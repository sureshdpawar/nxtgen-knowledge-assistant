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

from app.core.enums import UserRole
from app.models.agent import Agent
from app.models.user import User
from app.models.user_agent_access import (
    UserAgentAccess,
)


class AgentAccessService:

    def _get_agent(
        self,
        db: Session,
        current_user: User,
        agent_id: UUID,
    ) -> Agent:
        agent = db.get(
            Agent,
            agent_id,
        )

        if (
            agent is None
            or agent.tenant_id
            != current_user.tenant_id
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,
                detail="Agent not found.",
            )

        return agent

    def can_access_agent(
        self,
        db: Session,
        current_user: User,
        agent: Agent,
    ) -> bool:
        if (
            agent.tenant_id
            != current_user.tenant_id
        ):
            return False

        if (
            current_user.role
            == UserRole.ADMIN
        ):
            return True

        if (
            current_user.role
            != UserRole.USER
        ):
            return False

        stmt = (
            select(
                UserAgentAccess.id,
            )
            .where(
                UserAgentAccess.user_id
                == current_user.id,
                UserAgentAccess.agent_id
                == agent.id,
            )
            .limit(1)
        )

        return (
            db.scalar(stmt)
            is not None
        )

    def require_agent_access(
        self,
        db: Session,
        current_user: User,
        agent_id: UUID,
    ) -> Agent:
        agent = self._get_agent(
            db=db,
            current_user=current_user,
            agent_id=agent_id,
        )

        if not self.can_access_agent(
            db=db,
            current_user=current_user,
            agent=agent,
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,
                detail="Agent not found.",
            )

        return agent

    def list_user_ids(
        self,
        db: Session,
        current_user: User,
        agent_id: UUID,
    ) -> list[UUID]:
        agent = self._get_agent(
            db=db,
            current_user=current_user,
            agent_id=agent_id,
        )

        stmt = (
            select(
                UserAgentAccess.user_id,
            )
            .where(
                UserAgentAccess.agent_id
                == agent.id,
            )
            .order_by(
                UserAgentAccess.created_at,
            )
        )

        return list(
            db.scalars(stmt).all()
        )

    def replace_user_access(
        self,
        db: Session,
        current_user: User,
        agent_id: UUID,
        user_ids: list[UUID],
    ) -> list[UUID]:
        agent = self._get_agent(
            db=db,
            current_user=current_user,
            agent_id=agent_id,
        )

        unique_ids = list(
            dict.fromkeys(
                user_ids,
            )
        )

        if unique_ids:
            stmt = (
                select(
                    User.id,
                )
                .where(
                    User.id.in_(
                        unique_ids,
                    ),
                    User.tenant_id
                    == current_user.tenant_id,
                )
            )

            valid_ids = list(
                db.scalars(
                    stmt,
                ).all()
            )

            if (
                len(valid_ids)
                != len(unique_ids)
            ):
                raise HTTPException(
                    status_code=
                        status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "One or more users are "
                        "invalid for this tenant."
                    ),
                )

        db.execute(
            delete(
                UserAgentAccess,
            )
            .where(
                UserAgentAccess.agent_id
                == agent.id,
            )
        )

        db.flush()

        for user_id in unique_ids:
            db.add(
                UserAgentAccess(
                    user_id=user_id,
                    agent_id=agent.id,
                )
            )

        db.commit()

        return unique_ids

    def list_accessible_agents(
        self,
        db: Session,
        current_user: User,
    ) -> list[Agent]:
        if (
            current_user.role
            == UserRole.ADMIN
        ):
            stmt = (
                select(
                    Agent,
                )
                .where(
                    Agent.tenant_id
                    == current_user.tenant_id,
                )
                .order_by(
                    Agent.name,
                )
            )

            return list(
                db.scalars(
                    stmt,
                ).unique().all()
            )

        if (
            current_user.role
            != UserRole.USER
        ):
            return []

        stmt = (
            select(
                Agent,
            )
            .join(
                UserAgentAccess,
                UserAgentAccess.agent_id
                == Agent.id,
            )
            .where(
                UserAgentAccess.user_id
                == current_user.id,
                Agent.tenant_id
                == current_user.tenant_id,
            )
            .order_by(
                Agent.name,
            )
        )

        return list(
            db.scalars(
                stmt,
            ).unique().all()
        )
