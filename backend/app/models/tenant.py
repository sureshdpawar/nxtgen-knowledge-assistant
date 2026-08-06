from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin
from sqlalchemy.orm import relationship

class Tenant(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tenant"

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    plan: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="free",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
    )
    
    users = relationship(
    "User",
    back_populates="tenant",
    cascade="all, delete-orphan",
)