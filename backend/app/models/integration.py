from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
    JSON,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.core.enums import (
    IntegrationAuthType,
    IntegrationType,
)
from app.db.base import Base
from app.db.mixins import (
    TimestampMixin,
    UUIDMixin,
)


if TYPE_CHECKING:
    from app.models.tool_definition import (
        ToolDefinition,
    )


class Integration(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "integration"

    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "tenant.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    integration_type: Mapped[
        IntegrationType
    ] = mapped_column(
        Enum(
            IntegrationType,
        ),
        nullable=False,
        index=True,
    )

    base_url: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
    )

    auth_type: Mapped[
        IntegrationAuthType
    ] = mapped_column(
        Enum(
            IntegrationAuthType,
        ),
        default=
            IntegrationAuthType.NONE,
        server_default=
            IntegrationAuthType.NONE.value,
        nullable=False,
    )

    auth_config: Mapped[
        dict | None
    ] = mapped_column(
        JSON,
        nullable=True,
    )

    configuration: Mapped[
        dict | None
    ] = mapped_column(
        JSON,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
    )

    tools: Mapped[
        list["ToolDefinition"]
    ] = relationship(
        "ToolDefinition",
        back_populates="integration",
        cascade="all, delete-orphan",
    )