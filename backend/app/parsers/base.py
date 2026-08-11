from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

ParsedResult = dict[str, Any]


class BaseParser(ABC):
    """
    Base class for all document parsers.
    Every parser should extract plain text and return
    parser-specific metadata.
    """

    @abstractmethod
    def extract(
        self,
        file_path: Path,
    ) -> ParsedResult:
        """
        Extract text and metadata from a document.

        Returns:
            {
                "text": "...",
                "metadata": {
                    ...
                }
            }
        """
        pass