from app.models.knowledge_base import KnowledgeBase
from app.repositories.base_repository import BaseRepository


class KnowledgeBaseRepository(
    BaseRepository[KnowledgeBase],
):

    def __init__(self):
        super().__init__(KnowledgeBase)