from uuid import UUID

from pydantic import BaseModel

from app.core.enums import (
    KnowledgeBaseAccessLevel,
)


class KnowledgeBaseAccessAssignRequest(
    BaseModel
):
    access_level: KnowledgeBaseAccessLevel = (
        KnowledgeBaseAccessLevel.READ
    )


class KnowledgeBaseAccessResponse(
    BaseModel
):
    id: UUID
    user_id: UUID
    knowledge_base_id: UUID
    access_level: KnowledgeBaseAccessLevel

    model_config = {
        "from_attributes": True,
    }