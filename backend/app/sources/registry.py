from app.core.enums import (
    KnowledgeSourceType,
)
from app.sources.base import (
    KnowledgeSourceProvider,
)


class KnowledgeSourceProviderRegistry:

    def __init__(self):
        self._providers: dict[
            KnowledgeSourceType,
            KnowledgeSourceProvider,
        ] = {}

    def register(
        self,
        source_type: KnowledgeSourceType,
        provider: KnowledgeSourceProvider,
    ) -> None:

        self._providers[
            source_type
        ] = provider

    def get(
        self,
        source_type: KnowledgeSourceType,
    ) -> KnowledgeSourceProvider:

        provider = (
            self._providers
            .get(
                source_type
            )
        )

        if provider is None:
            raise ValueError(
                "No knowledge source provider "
                "registered for type "
                f"{source_type.value}"
            )

        return provider


provider_registry = (
    KnowledgeSourceProviderRegistry()
)


def register_default_providers(
) -> None:

    from app.sources.google_drive import (
        GoogleDriveProvider,
    )

    from app.sources.website import (
        WebsiteProvider,
    )

    provider_registry.register(
        KnowledgeSourceType.WEBSITE,
        WebsiteProvider(),
    )

    provider_registry.register(
        KnowledgeSourceType.GOOGLE_DRIVE,
        GoogleDriveProvider(),
    )


register_default_providers()