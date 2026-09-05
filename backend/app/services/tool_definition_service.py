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

from app.core.enums import (
    ToolExecutionPolicy,
    ToolType,
)
from app.models.agent import (
    Agent,
)
from app.models.agent_tool import (
    AgentTool,
)
from app.models.integration import (
    Integration,
)
from app.models.tool_definition import (
    ToolDefinition,
)
from app.models.user import User
from app.schemas.tool_definition import (
    ToolDefinitionCreate,
    ToolDefinitionUpdate,
)


class ToolDefinitionService:

    def _validate_integration(
        self,
        db: Session,
        tenant_id: UUID,
        integration_id: UUID | None,
    ) -> Integration | None:

        if integration_id is None:
            return None

        integration = db.get(
            Integration,
            integration_id,
        )

        if (
            integration is None
            or integration.tenant_id
            != tenant_id
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Invalid integration."
                ),
            )

        return integration

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

    def list(
        self,
        db: Session,
        current_user: User,
    ) -> list[ToolDefinition]:

        stmt = (
            select(
                ToolDefinition,
            )
            .where(
                ToolDefinition.tenant_id
                == current_user.tenant_id,
            )
            .order_by(
                ToolDefinition.name,
            )
        )

        return list(
            db.scalars(
                stmt,
            ).all()
        )

    def get(
        self,
        db: Session,
        current_user: User,
        tool_id: UUID,
    ) -> ToolDefinition:

        stmt = (
            select(
                ToolDefinition,
            )
            .where(
                ToolDefinition.id
                == tool_id,
                ToolDefinition.tenant_id
                == current_user.tenant_id,
            )
        )

        tool = (
            db.scalars(
                stmt,
            )
            .first()
        )

        if tool is None:
            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,
                detail=(
                    "Tool not found."
                ),
            )

        return tool

    def create(
        self,
        db: Session,
        current_user: User,
        payload: ToolDefinitionCreate,
    ) -> ToolDefinition:

        integration = (
            self._validate_integration(
                db=db,
                tenant_id=
                    current_user.tenant_id,
                integration_id=
                    payload.integration_id,
            )
        )

        if (
            payload.tool_type
            != ToolType.NATIVE
            and integration is None
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    "REST and MCP tools "
                    "require an integration."
                ),
            )

        if (
            payload.tool_type
            == ToolType.NATIVE
            and integration is not None
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Native tools cannot "
                    "be linked to an "
                    "integration."
                ),
            )

        tool = ToolDefinition(
            tenant_id=
                current_user.tenant_id,

            integration_id=
                payload.integration_id,

            name=
                payload.name.strip(),

            description=
                payload.description.strip(),

            tool_type=
                payload.tool_type,

            risk_level=
                payload.risk_level,

            input_schema=
                payload.input_schema,

            configuration=
                payload.configuration,

            is_active=
                payload.is_active,
        )

        db.add(
            tool,
        )

        db.commit()

        db.refresh(
            tool,
        )

        return tool

    def update(
        self,
        db: Session,
        current_user: User,
        tool_id: UUID,
        payload: ToolDefinitionUpdate,
    ) -> ToolDefinition:

        tool = self.get(
            db=db,
            current_user=
                current_user,
            tool_id=
                tool_id,
        )

        fields = (
            payload.model_fields_set
        )

        if "integration_id" in fields:
            integration = (
                self._validate_integration(
                    db=db,
                    tenant_id=
                        current_user.tenant_id,
                    integration_id=
                        payload.integration_id,
                )
            )

            if (
                tool.tool_type
                == ToolType.NATIVE
                and integration is not None
            ):
                raise HTTPException(
                    status_code=
                        status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Native tools cannot "
                        "be linked to an "
                        "integration."
                    ),
                )

            if (
                tool.tool_type
                != ToolType.NATIVE
                and integration is None
            ):
                raise HTTPException(
                    status_code=
                        status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "REST and MCP tools "
                        "require an integration."
                    ),
                )

            tool.integration_id = (
                payload.integration_id
            )

        if "name" in fields:
            if (
                payload.name is None
                or not payload.name.strip()
            ):
                raise HTTPException(
                    status_code=
                        status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Tool name is required."
                    ),
                )

            tool.name = (
                payload.name.strip()
            )

        if "description" in fields:
            if (
                payload.description
                is None
                or not
                payload.description.strip()
            ):
                raise HTTPException(
                    status_code=
                        status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Tool description "
                        "is required."
                    ),
                )

            tool.description = (
                payload.description.strip()
            )

        if (
            "risk_level" in fields
            and payload.risk_level
            is not None
        ):
            tool.risk_level = (
                payload.risk_level
            )

        if "input_schema" in fields:
            tool.input_schema = (
                payload.input_schema
                or {}
            )

        if "configuration" in fields:
            tool.configuration = (
                payload.configuration
            )

        if (
            "is_active" in fields
            and payload.is_active
            is not None
        ):
            tool.is_active = (
                payload.is_active
            )

        db.commit()

        db.refresh(
            tool,
        )

        return tool

    def delete(
        self,
        db: Session,
        current_user: User,
        tool_id: UUID,
    ) -> None:

        tool = self.get(
            db=db,
            current_user=
                current_user,
            tool_id=
                tool_id,
        )

        db.delete(
            tool,
        )

        db.commit()

    def assign_tools(
        self,
        db: Session,
        current_user: User,
        agent_id: UUID,
        tool_ids: list[UUID],
    ) -> list[ToolDefinition]:

        agent = self._get_agent(
            db=db,
            current_user=current_user,
            agent_id=agent_id,
        )

        unique_ids = list(
            dict.fromkeys(
                tool_ids,
            )
        )

        tools: list[
            ToolDefinition
        ] = []

        if unique_ids:
            stmt = (
                select(
                    ToolDefinition,
                )
                .where(
                    ToolDefinition.id.in_(
                        unique_ids,
                    ),
                    ToolDefinition.tenant_id
                    == current_user.tenant_id,
                    ToolDefinition.is_active
                    .is_(True),
                )
            )

            tools = list(
                db.scalars(
                    stmt,
                ).all()
            )

            if (
                len(tools)
                != len(unique_ids)
            ):
                raise HTTPException(
                    status_code=
                        status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "One or more tools "
                        "are invalid or inactive."
                    ),
                )

        existing_links = list(
            db.scalars(
                select(
                    AgentTool,
                )
                .where(
                    AgentTool.agent_id
                    == agent.id,
                )
            ).all()
        )

        existing_policies = {
            link.tool_id:
                link.execution_policy
            for link in existing_links
        }

        db.execute(
            delete(
                AgentTool,
            )
            .where(
                AgentTool.agent_id
                == agent.id,
            )
        )

        db.flush()

        for tool_id in unique_ids:
            db.add(
                AgentTool(
                    agent_id=
                        agent.id,
                    tool_id=
                        tool_id,
                    execution_policy=(
                        existing_policies.get(
                            tool_id,
                            ToolExecutionPolicy
                            .HUMAN_APPROVAL,
                        )
                    ),
                )
            )

        db.commit()

        return tools

    def list_agent_tool_policies(
        self,
        db: Session,
        current_user: User,
        agent_id: UUID,
    ) -> list[AgentTool]:
        agent = self._get_agent(
            db=db,
            current_user=current_user,
            agent_id=agent_id,
        )

        stmt = (
            select(
                AgentTool,
            )
            .where(
                AgentTool.agent_id
                == agent.id,
            )
            .order_by(
                AgentTool.created_at,
            )
        )

        return list(
            db.scalars(
                stmt,
            ).all()
        )

    def update_agent_tool_policy(
        self,
        db: Session,
        current_user: User,
        agent_id: UUID,
        tool_id: UUID,
        execution_policy:
            ToolExecutionPolicy,
    ) -> AgentTool:
        agent = self._get_agent(
            db=db,
            current_user=current_user,
            agent_id=agent_id,
        )

        stmt = (
            select(
                AgentTool,
            )
            .join(
                ToolDefinition,
                ToolDefinition.id
                == AgentTool.tool_id,
            )
            .where(
                AgentTool.agent_id
                == agent.id,
                AgentTool.tool_id
                == tool_id,
                ToolDefinition.tenant_id
                == current_user.tenant_id,
            )
        )

        link = (
            db.scalars(
                stmt,
            ).first()
        )

        if link is None:
            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,
                detail=(
                    "Tool is not assigned "
                    "to this agent."
                ),
            )

        link.execution_policy = (
            execution_policy
        )

        db.commit()
        db.refresh(link)

        return link
