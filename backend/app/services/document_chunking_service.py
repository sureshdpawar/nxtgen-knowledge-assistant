from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)


class DocumentChunkingService:

    STRATEGY_NAME = (
        "recursive-character-v1"
    )

    @property
    def strategy_name(
        self,
    ) -> str:
        return (
            self.STRATEGY_NAME
        )

    def chunk(
        self,
        pages: list[dict],
        chunk_size: int,
        chunk_overlap: int,
    ) -> list[dict]:

        self._validate_configuration(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        splitter = (
            RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                is_separator_regex=False,
            )
        )

        chunks: list[dict] = []

        for page in pages:

            page_number = (
                page.get(
                    "page",
                    1,
                )
            )

            text = (
                page.get(
                    "text",
                    ""
                )
                or ""
            )

            text = (
                text.strip()
            )

            if not text:
                continue

            page_chunks = (
                splitter.split_text(
                    text
                )
            )

            for chunk_text in page_chunks:

                clean_text = (
                    chunk_text.strip()
                )

                if not clean_text:
                    continue

                chunks.append(
                    {
                        "text":
                            clean_text,

                        "page":
                            page_number,
                    }
                )

        return chunks

    def _validate_configuration(
        self,
        chunk_size: int,
        chunk_overlap: int,
    ) -> None:

        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be "
                "greater than 0."
            )

        if chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap cannot "
                "be negative."
            )

        if (
            chunk_overlap
            >= chunk_size
        ):
            raise ValueError(
                "chunk_overlap must be "
                "smaller than chunk_size."
            )