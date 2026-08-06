from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    repr_cols_num = 3

    def __repr__(self) -> str:

        values = []

        for column in list(self.__table__.columns)[: self.repr_cols_num]:
            values.append(
                f"{column.name}={getattr(self, column.name)!r}"
            )

        return f"<{self.__class__.__name__}({', '.join(values)})>"