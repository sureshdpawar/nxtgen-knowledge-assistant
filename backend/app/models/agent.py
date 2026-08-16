from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.core.enums import (
    AgentStatus,
)
from app.db.base import Base
from app.db.mixins import (
    TimestampMixin,
    UUIDMixin,
)


if TYPE_CHECKING:
    from app.models.agent_knowledge_base import (
        AgentKnowledgeBase,
    )
    from app.models.tenant_llm_configuration import (
        TenantLLMConfiguration,
    )
    from app.models.user import (
        User,
    )


class Agent(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "agent"

    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "tenant.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    created_by: Mapped[UUID] = mapped_column(
        ForeignKey(
            "app_user.id",
        ),
        nullable=False,
        index=True,
    )

    llm_configuration_id: Mapped[
        UUID | None
    ] = mapped_column(
        ForeignKey(
            "tenant_llm_configuration.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    system_prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    max_iterations: Mapped[int] = mapped_column(
        Integer,
        default=6,
        server_default="6",
        nullable=False,
    )

    status: Mapped[
        AgentStatus
    ] = mapped_column(
        Enum(
            AgentStatus,
        ),
        default=
            AgentStatus.DRAFT,
        server_default=
            AgentStatus.DRAFT.value,
        nullable=False,
    )

    creator: Mapped[
        "User"
    ] = relationship(
        "User",
    )

    llm_configuration: Mapped[
        "TenantLLMConfiguration | None"
    ] = relationship(
        "TenantLLMConfiguration",
    )

    knowledge_base_links: Mapped[
        list[
            "AgentKnowledgeBase"
        ]
    ] = relationship(
        "AgentKnowledgeBase",
        back_populates="agent",
        cascade=(
            "all, "
            "delete-orphan"
        ),
    )

    @property
    def knowledge_base_ids(
        self,
    ) -> list[UUID]:
        return [
            link.knowledge_base_id
            for link
            in self.knowledge_base_links
        ]