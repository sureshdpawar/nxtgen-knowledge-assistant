from uuid import UUID

from sqlalchemy import (
    Boolean,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.core.enums import LLMProvider
from app.db.base import Base
from app.db.mixins import (
    TimestampMixin,
    UUIDMixin,
)


class TenantLLMConfiguration(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "tenant_llm_configuration"

    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenant.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="Default",
        server_default="Default",
    )

    provider: Mapped[LLMProvider] = mapped_column(
        Enum(LLMProvider),
        nullable=False,
    )

    model_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    base_url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    api_key: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    temperature: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    max_tokens: Mapped[int] = mapped_column(
        Integer,
        default=2048,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
    )

    tenant: Mapped["Tenant"] = relationship(
        "Tenant",
        back_populates="llm_configurations",
    )

    knowledge_bases: Mapped[
        list["KnowledgeBase"]
    ] = relationship(
        "KnowledgeBase",
        back_populates="llm_configuration",
    )