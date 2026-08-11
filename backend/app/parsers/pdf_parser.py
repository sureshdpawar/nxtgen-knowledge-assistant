from pathlib import Path

import pymupdf

from app.parsers.base import BaseParser, ParsedResult


class PdfParser(BaseParser):

    def extract(
        self,
        file_path: Path,
    ) -> ParsedResult:

        document = pymupdf.open(file_path)

        pages = []

        for page in document:
            pages.append(page.get_text())

        document.close()

        text = "\n".join(pages)

        return {
            "text": text,
            "metadata": {
                "page_count": len(pages),
            },
        }