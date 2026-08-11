from app.models.conversation import Conversation
from app.repositories.base_repository import BaseRepository


class ConversationRepository(
    BaseRepository[Conversation],
):

    def __init__(self):
        super().__init__(Conversation)