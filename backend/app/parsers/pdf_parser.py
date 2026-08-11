from pathlib import Path

import pymupdf

from app.parsers.base import (
    BaseParser,
    ParsedResult,
)


class PdfParser(BaseParser):

    def extract(
        self,
        file_path: Path,
    ) -> ParsedResult:

        document = pymupdf.open(file_path)

        pages = []

        for index, page in enumerate(document):

            pages.append(
                {
                    "page": index + 1,
                    "text": page.get_text(),
                }
            )

        document.close()

        return {
            "pages": pages,
            "metadata": {
                "page_count": len(pages),
            },
        }