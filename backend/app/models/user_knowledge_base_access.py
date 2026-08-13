from uuid import UUID

from sqlalchemy import (
    Enum,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.core.enums import (
    KnowledgeBaseAccessLevel,
)
from app.db.base import Base
from app.db.mixins import (
    TimestampMixin,
    UUIDMixin,
)
from app.models.knowledge_base import (
    KnowledgeBase,
)
from app.models.user import (
    User,
)


class UserKnowledgeBaseAccess(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = (
        "user_knowledge_base_access"
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "knowledge_base_id",
            name="uq_user_knowledge_base_access",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("app_user.id"),
        nullable=False,
        index=True,
    )

    knowledge_base_id: Mapped[UUID] = mapped_column(
        ForeignKey("knowledge_base.id"),
        nullable=False,
        index=True,
    )

    access_level: Mapped[
        KnowledgeBaseAccessLevel
    ] = mapped_column(
        Enum(
            KnowledgeBaseAccessLevel
        ),
        default=
            KnowledgeBaseAccessLevel.READ,
        server_default=
            KnowledgeBaseAccessLevel.READ.value,
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
    )

    knowledge_base: Mapped[
        "KnowledgeBase"
    ] = relationship(
        "KnowledgeBase",
    )