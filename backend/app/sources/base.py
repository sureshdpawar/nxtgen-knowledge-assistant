from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.models.knowledge_source import KnowledgeSource
from app.sources.source_item import SourceItem


@dataclass(slots=True)
class SourceDiscoveryResult:
    """
    Result of provider discovery plus reconciliation safety metadata.

    `authoritative` means the provider used an inventory that is intended
    to represent the complete source (for example, a sitemap).

    `complete` means that inventory was not truncated and all selected
    items were successfully fetched/extracted.

    Missing-item reconciliation is safe only when both are true.
    """

    items: list[SourceItem]
    strategy: str = "provider"
    authoritative: bool = True
    complete: bool = True
    discovered_url_count: int = 0
    failed_url_count: int = 0
    warnings: list[str] = field(default_factory=list)

    @property
    def allow_missing_reconciliation(self) -> bool:
        return self.authoritative and self.complete


class KnowledgeSourceProvider(ABC):

    @abstractmethod
    def discover(
        self,
        source: KnowledgeSource,
    ) -> list[SourceItem]:
        """
        Discover and return the current items available from a knowledge source.

        Providers are responsible for connecting to the source, discovering
        items, downloading/exporting content, generating stable external IDs
        and checksums, and returning normalized SourceItem objects.

        Providers must not create Document rows, create ingestion jobs, chunk
        content, generate embeddings, or update KnowledgeSourceSync state.
        """
        raise NotImplementedError

    def discover_result(
        self,
        source: KnowledgeSource,
    ) -> SourceDiscoveryResult:
        """
        Backward-compatible discovery contract.

        Existing providers keep their current authoritative reconciliation
        semantics unless they override this method with richer safety metadata.
        """
        items = self.discover(source)

        return SourceDiscoveryResult(
            items=items,
            strategy="provider",
            authoritative=True,
            complete=True,
            discovered_url_count=len(items),
        )
