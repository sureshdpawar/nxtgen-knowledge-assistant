from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class SourceItem:
    external_id: str

    title: str

    mime_type: str

    checksum: str

    source_url: str | None = None

    modified_at: datetime | None = None

    filename: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    content: bytes | None = None