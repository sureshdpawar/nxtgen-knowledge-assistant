from pathlib import Path

from app.parsers.pdf_parser import PdfParser


class ParserFactory:

    @staticmethod
    def get_parser(
        file_path: Path,
    ):

        extension = file_path.suffix.lower()

        if extension == ".pdf":
            return PdfParser()

        raise ValueError(
            f"No parser available for {extension}"
        )