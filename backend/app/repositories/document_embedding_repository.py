from app.models.document_embedding import DocumentEmbedding
from app.repositories.base_repository import BaseRepository


class DocumentEmbeddingRepository(
    BaseRepository[DocumentEmbedding],
):

    def __init__(self):
        super().__init__(DocumentEmbedding)