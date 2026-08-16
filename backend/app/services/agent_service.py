from uuid import UUID

from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.agent_knowledge_base import (
    AgentKnowledgeBase,
)
from app.models.knowledge_base import (
    KnowledgeBase,
)
from app.models.tenant_llm_configuration import (
    TenantLLMConfiguration,
)
from app.models.user import User
from app.repositories.agent_repository import (
    AgentRepository,
)
from app.schemas.agent import (
    AgentCreate,
    AgentUpdate,
)


class AgentService:

    def __init__(self):
        self.repository = (
            AgentRepository()
        )

    def _validate_llm_configuration(
        self,
        db: Session,
        tenant_id: UUID,
        configuration_id:
            UUID | None,
    ) -> None:

        if configuration_id is None:
            return

        configuration = db.get(
            TenantLLMConfiguration,
            configuration_id,
        )

        if (
            configuration is None
            or configuration.tenant_id
            != tenant_id
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Invalid LLM "
                    "configuration."
                ),
            )

        if not configuration.is_active:
            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    "LLM configuration "
                    "must be active."
                ),
            )

    def _validate_knowledge_bases(
        self,
        db: Session,
        tenant_id: UUID,
        knowledge_base_ids:
            list[UUID],
    ) -> list[KnowledgeBase]:

        if not knowledge_base_ids:
            return []

        unique_ids = list(
            set(
                knowledge_base_ids,
            )
        )

        stmt = (
            select(
                KnowledgeBase,
            )
            .where(
                KnowledgeBase.id.in_(
                    unique_ids,
                ),
                KnowledgeBase.tenant_id
                == tenant_id,
            )
        )

        knowledge_bases = list(
            db.scalars(
                stmt,
            ).all()
        )

        if (
            len(knowledge_bases)
            != len(unique_ids)
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,
                detail=(
                    "One or more knowledge "
                    "bases are invalid."
                ),
            )

        return knowledge_bases

    def _replace_knowledge_bases(
        self,
        db: Session,
        agent: Agent,
        knowledge_base_ids:
            list[UUID],
    ) -> None:

        self._validate_knowledge_bases(
            db=db,
            tenant_id=
                agent.tenant_id,
            knowledge_base_ids=
                knowledge_base_ids,
        )

        agent.knowledge_base_links.clear()

        db.flush()

        for knowledge_base_id in (
            dict.fromkeys(
                knowledge_base_ids,
            )
        ):
            agent.knowledge_base_links.append(
                AgentKnowledgeBase(
                    knowledge_base_id=
                        knowledge_base_id,
                )
            )

    def list(
        self,
        db: Session,
        current_user: User,
    ) -> list[Agent]:

        return (
            self.repository
            .list_by_tenant(
                db=db,
                tenant_id=
                    current_user.tenant_id,
            )
        )

    def get(
        self,
        db: Session,
        current_user: User,
        agent_id: UUID,
    ) -> Agent:

        agent = (
            self.repository
            .get_by_id_and_tenant(
                db=db,
                tenant_id=
                    current_user.tenant_id,
                agent_id=
                    agent_id,
            )
        )

        if agent is None:
            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,
                detail=(
                    "Agent not found."
                ),
            )

        return agent

    def create(
        self,
        db: Session,
        current_user: User,
        payload: AgentCreate,
    ) -> Agent:

        self._validate_llm_configuration(
            db=db,
            tenant_id=
                current_user.tenant_id,
            configuration_id=
                payload.llm_configuration_id,
        )

        self._validate_knowledge_bases(
            db=db,
            tenant_id=
                current_user.tenant_id,
            knowledge_base_ids=
                payload.knowledge_base_ids,
        )

        agent = Agent(
            tenant_id=
                current_user.tenant_id,

            created_by=
                current_user.id,

            name=
                payload.name.strip(),

            description=
                (
                    payload.description.strip()
                    if payload.description
                    else None
                ),

            system_prompt=
                payload.system_prompt.strip(),

            llm_configuration_id=
                payload.llm_configuration_id,

            max_iterations=
                payload.max_iterations,

            status=
                payload.status,
        )

        db.add(
            agent,
        )

        db.flush()

        self._replace_knowledge_bases(
            db=db,
            agent=agent,
            knowledge_base_ids=
                payload.knowledge_base_ids,
        )

        db.commit()

        return self.get(
            db=db,
            current_user=
                current_user,
            agent_id=
                agent.id,
        )

    def update(
        self,
        db: Session,
        current_user: User,
        agent_id: UUID,
        payload: AgentUpdate,
    ) -> Agent:

        agent = self.get(
            db=db,
            current_user=
                current_user,
            agent_id=
                agent_id,
        )

        fields_set = (
            payload.model_fields_set
        )

        if "name" in fields_set:
            if (
                payload.name is None
                or not payload.name.strip()
            ):
                raise HTTPException(
                    status_code=
                        status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Agent name "
                        "is required."
                    ),
                )

            agent.name = (
                payload.name.strip()
            )

        if "description" in fields_set:
            agent.description = (
                payload.description.strip()
                if payload.description
                else None
            )

        if "system_prompt" in fields_set:
            if (
                payload.system_prompt
                is None
                or not
                payload.system_prompt.strip()
            ):
                raise HTTPException(
                    status_code=
                        status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "System prompt "
                        "is required."
                    ),
                )

            agent.system_prompt = (
                payload.system_prompt.strip()
            )

        if (
            "llm_configuration_id"
            in fields_set
        ):
            self._validate_llm_configuration(
                db=db,
                tenant_id=
                    current_user.tenant_id,
                configuration_id=
                    payload
                    .llm_configuration_id,
            )

            agent.llm_configuration_id = (
                payload
                .llm_configuration_id
            )

        if (
            "max_iterations"
            in fields_set
            and payload.max_iterations
            is not None
        ):
            agent.max_iterations = (
                payload.max_iterations
            )

        if (
            "status"
            in fields_set
            and payload.status
            is not None
        ):
            agent.status = (
                payload.status
            )

        if (
            "knowledge_base_ids"
            in fields_set
        ):
            self._replace_knowledge_bases(
                db=db,
                agent=agent,
                knowledge_base_ids=
                    (
                        payload
                        .knowledge_base_ids
                        or []
                    ),
            )

        db.commit()

        return self.get(
            db=db,
            current_user=
                current_user,
            agent_id=
                agent.id,
        )

    def delete(
        self,
        db: Session,
        current_user: User,
        agent_id: UUID,
    ) -> None:

        agent = self.get(
            db=db,
            current_user=
                current_user,
            agent_id=
                agent_id,
        )

        db.delete(
            agent,
        )

        db.commit()