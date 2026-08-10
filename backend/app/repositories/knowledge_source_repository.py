from app.models.knowledge_source import KnowledgeSource
from app.repositories.base_repository import BaseRepository


class KnowledgeSourceRepository(
    BaseRepository[KnowledgeSource],
):

    def __init__(self):
        super().__init__(KnowledgeSource)