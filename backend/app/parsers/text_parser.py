from pathlib import Path

from app.parsers.base import (
    BaseParser,
    ParsedResult,
)


class TextParser(BaseParser):

    def extract(
        self,
        file_path: Path,
    ) -> ParsedResult:

        text = file_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        return {
            "pages": [
                {
                    "page": 1,
                    "text": text,
                }
            ],
            "metadata": {
                "page_count": 1,
            },
        }