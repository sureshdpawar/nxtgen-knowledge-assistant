from app.core.config import settings


class DocumentChunkingService:

    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP

    def chunk(
        self,
        text: str,
    ) -> list[str]:

        chunks = []

        start = 0

        while start < len(text):

            end = start + self.chunk_size

            chunks.append(
                text[start:end]
            )

            start = end - self.chunk_overlap

        return chunks