from pathlib import Path

from app.parsers.docx_parser import (
    DocxParser,
)
from app.parsers.pdf_parser import (
    PdfParser,
)
from app.parsers.pptx_parser import (
    PptxParser,
)
from app.parsers.text_parser import (
    TextParser,
)
from app.parsers.xlsx_parser import (
    XlsxParser,
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

        if extension == ".docx":
            return DocxParser()

        if extension == ".pptx":
            return PptxParser()

        if extension == ".xlsx":
            return XlsxParser()

        if extension in {
            ".txt",
            ".md",
            ".csv",
        }:
            return TextParser()

        raise ValueError(
            "No parser available for "
            f"{extension}"
        )