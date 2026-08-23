class DocumentChunkingService:

    def chunk(
        self,
        pages: list[dict],
        chunk_size: int,
        chunk_overlap: int,
    ) -> list[dict]:

        chunks = []

        for page in pages:

            page_number = page["page"]
            text = page["text"]

            start = 0

            while start < len(text):

                end = (
                    start
                    + chunk_size
                )

                chunks.append(
                    {
                        "text":
                            text[
                                start:end
                            ],
                        "page":
                            page_number,
                    }
                )

                start = (
                    end
                    - chunk_overlap
                )

        return chunks