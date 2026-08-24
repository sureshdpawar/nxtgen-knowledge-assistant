from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from app.core.enums import (
    KnowledgeBaseStatus,
    KnowledgeBaseVisibility,
)


class KnowledgeBaseCreate(BaseModel):
    name: str
    description: str | None = None

    visibility: KnowledgeBaseVisibility = (
        KnowledgeBaseVisibility.PRIVATE
    )

    #
    # Optional KB-level RAG overrides.
    #
    # None means:
    # use the platform default.
    #
    chunk_size: int | None = Field(
        default=None,
        ge=100,
        le=4000,
    )

    chunk_overlap: int | None = Field(
        default=None,
        ge=0,
        le=1000,
    )

    top_k: int | None = Field(
        default=None,
        ge=1,
        le=20,
    )

    @model_validator(
        mode="after",
    )
    def validate_chunking(
        self,
    ):
        if (
            self.chunk_size
            is not None
            and self.chunk_overlap
            is not None
            and self.chunk_overlap
            >= self.chunk_size
        ):
            raise ValueError(
                "chunk_overlap must be "
                "less than chunk_size."
            )

        return self


class KnowledgeBaseUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

    status: (
        KnowledgeBaseStatus
        | None
    ) = None

    visibility: (
        KnowledgeBaseVisibility
        | None
    ) = None

    #
    # Optional KB-level RAG overrides.
    #
    # Setting a value to None allows
    # the KB to fall back to the
    # platform default.
    #
    chunk_size: int | None = Field(
        default=None,
        ge=100,
        le=4000,
    )

    chunk_overlap: int | None = Field(
        default=None,
        ge=0,
        le=1000,
    )

    top_k: int | None = Field(
        default=None,
        ge=1,
        le=20,
    )

    @model_validator(
        mode="after",
    )
    def validate_chunking(
        self,
    ):
        if (
            self.chunk_size
            is not None
            and self.chunk_overlap
            is not None
            and self.chunk_overlap
            >= self.chunk_size
        ):
            raise ValueError(
                "chunk_overlap must be "
                "less than chunk_size."
            )

        return self


class KnowledgeBaseResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    tenant_id: UUID
    owner_user_id: UUID

    llm_configuration_id: (
        UUID
        | None
    )

    name: str
    description: str | None

    #
    # KB-level overrides.
    #
    # None means the KB currently
    # inherits the platform default.
    #
    chunk_size: int | None
    chunk_overlap: int | None
    top_k: int | None

    status: KnowledgeBaseStatus
    visibility: KnowledgeBaseVisibility

    created_at: datetime
    updated_at: datetime