from app.models.conversation_message import (
    ConversationMessage,
)
from app.repositories.base_repository import (
    BaseRepository,
)


class ConversationMessageRepository(
    BaseRepository[ConversationMessage],
):

    def __init__(self):
        super().__init__(ConversationMessage)