from sentence_transformers import SentenceTransformer

from app.core.constants import EMBEDDING_MODEL


class EmbeddingService:

    def embed(
        self,
        text: str,
    ) -> list[float]:

        model = SentenceTransformer(
            EMBEDDING_MODEL,
        )

        embedding = model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()