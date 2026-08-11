from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

ParsedPage = dict[str, Any]
ParsedResult = dict[str, Any]


class BaseParser(ABC):
    """
    Base class for all document parsers.

    Every parser should extract page-wise text and return
    parser-specific metadata.
    """

    @abstractmethod
    def extract(
        self,
        file_path: Path,
    ) -> ParsedResult:
        """
        Extract pages and metadata from a document.

        Returns:

        {
            "pages": [
                {
                    "page": 1,
                    "text": "..."
                },
                {
                    "page": 2,
                    "text": "..."
                }
            ],
            "metadata": {
                ...
            }
        }
        """
        pass