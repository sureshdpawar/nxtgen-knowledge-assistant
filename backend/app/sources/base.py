from abc import (
    ABC,
    abstractmethod,
)

from app.models.knowledge_source import (
    KnowledgeSource,
)
from app.sources.source_item import (
    SourceItem,
)


class KnowledgeSourceProvider(
    ABC
):

    @abstractmethod
    def discover(
        self,
        source: KnowledgeSource,
    ) -> list[SourceItem]:
        """
        Discover and return the current items
        available from a knowledge source.

        Providers are responsible for:

        - connecting to the external source
        - discovering items
        - downloading/exporting content
        - generating a stable external_id
        - generating a checksum/fingerprint
        - returning normalized SourceItem objects

        Providers must NOT:

        - create Document rows
        - create ingestion jobs
        - chunk content
        - generate embeddings
        - update KnowledgeSourceSync state
        """
        raise NotImplementedError