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

from app.core.config import settings
from app.core.enums import (
    KnowledgeBaseStatus,
    KnowledgeBaseVisibility,
)
from app.db.base import Base
from app.db.mixins import (
    TimestampMixin,
    UUIDMixin,
)


class KnowledgeBase(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "knowledge_base"

    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenant.id"),
        nullable=False,
        index=True,
    )

    owner_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("app_user.id"),
        nullable=False,
        index=True,
    )

    llm_configuration_id: Mapped[
        UUID | None
    ] = mapped_column(
        ForeignKey(
            "tenant_llm_configuration.id",
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

    
    chunk_size: Mapped[
        int | None
    ] = mapped_column(
        Integer,
        nullable=True,
    )

    chunk_overlap: Mapped[
        int | None
    ] = mapped_column(
        Integer,
        nullable=True,
    )

    top_k: Mapped[
        int | None
    ] = mapped_column(
        Integer,
        nullable=True,
    )

    status: Mapped[
        KnowledgeBaseStatus
    ] = mapped_column(
        Enum(
            KnowledgeBaseStatus,
        ),
        default=
            KnowledgeBaseStatus.ACTIVE,
        server_default=
            KnowledgeBaseStatus.ACTIVE.value,
        nullable=False,
    )

    visibility: Mapped[
        KnowledgeBaseVisibility
    ] = mapped_column(
        Enum(
            KnowledgeBaseVisibility,
        ),
        default=
            KnowledgeBaseVisibility.PRIVATE,
        server_default=
            KnowledgeBaseVisibility.PRIVATE.value,
        nullable=False,
    )

    @property
    def effective_chunk_size(
        self,
    ) -> int:
        return (
            self.chunk_size
            if self.chunk_size
            is not None
            else settings.CHUNK_SIZE
        )

    @property
    def effective_chunk_overlap(
        self,
    ) -> int:
        return (
            self.chunk_overlap
            if self.chunk_overlap
            is not None
            else settings.CHUNK_OVERLAP
        )

    @property
    def effective_top_k(
        self,
    ) -> int:
        return (
            self.top_k
            if self.top_k
            is not None
            else settings.TOP_K
        )

    tenant: Mapped["Tenant"] = relationship(
        "Tenant",
        back_populates="knowledge_bases",
    )

    owner: Mapped["User"] = relationship(
        "User",
        back_populates="owned_knowledge_bases",
    )

    llm_configuration: Mapped[
        "TenantLLMConfiguration | None"
    ] = relationship(
        "TenantLLMConfiguration",
        back_populates="knowledge_bases",
    )

    knowledge_sources: Mapped[
        list["KnowledgeSource"]
    ] = relationship(
        "KnowledgeSource",
        back_populates="knowledge_base",
        cascade="all, delete-orphan",
    )