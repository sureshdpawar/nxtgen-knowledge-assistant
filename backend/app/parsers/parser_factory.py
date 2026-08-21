from pathlib import Path

from app.parsers.pdf_parser import (
    PdfParser,
)
from app.parsers.text_parser import (
    TextParser,
)


class ParserFactory:

    @staticmethod
    def get_parser(
        file_path: Path,
    ):

        extension = (
            file_path
            .suffix
            .lower()
        )

        if extension == ".pdf":
            return PdfParser()

        if extension in {
            ".txt",
            ".md",
        }:
            return TextParser()

        raise ValueError(
            f"No parser available for "
            f"{extension}"
        )